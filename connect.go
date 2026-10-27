package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"strconv"
	"strings"
	"time"
)

func ping(conn net.Conn) error {
	log.Println("pinging", conn.RemoteAddr())
	conn.SetWriteDeadline(time.Now().Add(5 * time.Second))
	_, err := conn.Write([]byte("ping"))
	if err != nil {
		return err
	}

	pong := make([]byte, 4)
	conn.SetDeadline(time.Now().Add(5 * time.Second))
	_, err = conn.Read(pong)
	if err != nil && err != io.EOF {
		return err
	}
	if string(pong) != "pong" {
		return fmt.Errorf("Wrong pong message: %s", pong)
	}
	log.Println(string(pong))
	return nil
}

func serverWithPinger() {
	listener, err := net.Listen("tcp", "127.0.0.1:")
	if err != nil {
		log.Fatalln(err)
	}
	defer listener.Close()
	log.Printf("listening on %q", listener.Addr())

	type connection struct {
		conn net.Conn
		err  error
	}
	stop := make(chan struct{})

	// Wait for connections
	for {
		c := make(chan connection)
		go func(c chan connection) {
			conn, err := listener.Accept()
			c <- connection{conn, err}
		}(c)
		connerr := connection{}
		select {
		case connerr = <-c:
		case <-stop:
			return
		}
		conn, err := connerr.conn, connerr.err
		if err != nil {
			log.Fatalln(err)
		}
		go func() {
			defer func() {
				log.Println("closing connection to", conn.RemoteAddr())
				conn.Close()
			}()
			for {
				message := ""
				// Inquisitive Heartbeat Loop
				for {
					conn.SetReadDeadline(time.Now().Add(10 * time.Second))
					buf := make([]byte, 1024)
					n, err := conn.Read(buf)
					if err != nil {
						nErr, ok := err.(net.Error)
						if ok && nErr.Timeout() {
							err := ping(conn)
							if err != nil {
								log.Println(err)
								return
							} else {
								continue
							}
						} else {
							log.Println(err)
							return
						}
					} else {
						message = string(buf[:n])
						break
					}
				}
				log.Printf("received: %q from %s", message, conn.RemoteAddr())
				if message == "close" {
					log.Printf("closing...")
					stop <- struct{}{}
					return
				}
			}
		}()
	}
}

func ponger(ctx context.Context, conn net.Conn) {
	// Responsive Heartbeat loop
	for {
		select {
		case <-ctx.Done():
			log.Println("closed ponger")
			return
		default:
			ping := make([]byte, 4)
			conn.SetReadDeadline(time.Now().Add(5 * time.Second))
			conn.Read(ping)
			if string(ping) == "ping" {
				log.Println(string(ping))
				conn.SetWriteDeadline(time.Now().Add(5 * time.Second))
				conn.Write([]byte("pong"))
				log.Println("ponging", conn.RemoteAddr())
			}
		}
	}
}

func clientWithPonger() {
	var port string
	fmt.Println("What is the port of the listener")
	fmt.Scan(&port)
	conn, err := net.DialTimeout("tcp", "127.0.0.1:"+port, 5*time.Second)
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	go ponger(ctx, conn)

	var message string
	for message != "close" && message != "exit" {
		fmt.Println("Write a message for the listener")
		fmt.Scan(&message)
		conn.Write([]byte(message))
	}
	fmt.Println("Closed")
}

const (
	groupSoc string = "230.1.1.1:5000"
)

// userName is the userName of this user.
var userName string

// ip2Idx maps IP address strings
// to their index in [currentPlayers].
var ip2Idx map[string]int = make(map[string]int)

// currentPlayers stores all the currently available user as [*user]s
// except this user.
var currentPlayers []*user

// chosenIndex is the index of the chosen opponent [*user]
// in [currentPlayers].
//
// It is negative(-1) when an opponent has not been chosen.
var chosenIndex int = -1

// chosenOpponent is the channel for sending and
// receiving the chosen opponent [*user]
// either from [currentPlayers] or
// from a connection request sent by another player.
var chosenOpponent chan *user = make(chan *user)

// prospectiveOpponent is the channel for sending and
// receiving a prospective opponent [*user]
// from the [currentPlayers] list.
var prospectiveOpponent chan *user = make(chan *user)

// opponent is the chosen opponent
var opponent *user

// replyChan is the channel for sending and
// receiving the reply to a connection request
// from another player
var replyChan chan string = make(chan string)

// imUnavailable sends a "d-" message to the group
// telling all group listeners that the user is unavailable
// and should be removed from their [currentPlayers] lists
// if the user was present in the list.
func imUnavailable(gdconn *net.UDPConn, gaddr *net.UDPAddr) {
	// Tell the group you're not available
	_, err := gdconn.WriteToUDP([]byte("d-"), gaddr)
	if err != nil {
		log.Panic(err)
	}
}

// iAmAvailable sends a "p-" message to the group
// telling all group listeners that the user is available
// and should be added to their [currentPlayers] lists
// if the user was not present in the list.
func iAmAvailable(gdconn *net.UDPConn, gaddr *net.UDPAddr) {
	// Tell the group you are available

	_, err := gdconn.WriteToUDP([]byte("p-"+userName), gaddr)
	if err != nil {
		log.Panic(err)
	}
}

func listenForAUnicastMessageAndReply(conn *net.UDPConn) {
	buff := make([]byte, 1024)
	n, raddr, err := conn.ReadFromUDP(buff)
	if err != nil {
		if errors.Is(err, net.ErrClosed) {
			return
		}
		log.Panic(err)
	}
	message := string(buff[:n])
	command := message[:2]

	isReplyFromChosenPlayer := chosenIndex >= 0 && raddr.String() == currentPlayers[chosenIndex].ipAddr.String()
	switch command {
	// Recieved Reply (Yes/No) from a player that you chose
	case "y-":
		if isReplyFromChosenPlayer {
			// Choose player
			chosenOpponent <- currentPlayers[chosenIndex]
			log.Println("Playing with ", currentPlayers[chosenIndex].userName, " at", raddr)
		}
	case "n-":
		if isReplyFromChosenPlayer {
			// Deselect the currently chosen player
			log.Println("Deselecting", chosenIndex, currentPlayers[chosenIndex])
			chosenIndex = -1
			chosenOpponent <- nil
		}

	// Connection Request from a player that chose you
	case "i-":
		playerName := message[2:]
		log.Println("Received Connection Request from", playerName, raddr)
		fmt.Println("Accept Connection Request from", playerName, raddr, "?")
		fmt.Print("Y/n: ")
		// Inputted reply is sent on reply channel
		if "y" == <-replyChan {
			// Reply: Tell the player you accept
			_, err := conn.WriteToUDP([]byte("y-"), raddr)
			if err != nil {
				log.Panicln(err)
			}

			// Choose player
			log.Println("Blocking for chosenOpponent")
			chosenOpponent <- &user{playerName, raddr}
			// opponent = &user{playerName, raddr}
			log.Println("Sent chosenOpponent")
			log.Println("Playing with", playerName, "at", raddr)
		} else {
			// Reply: Tell the player you reject
			_, err := conn.WriteToUDP([]byte("n-"), raddr)
			if err != nil {
				log.Panicln(err)
			}
			chosenOpponent <- nil
			log.Println("Rejected", playerName, "at", raddr)
		}
	}
}

// Obsolete
func waitToBeChosen(ctx context.Context, conn net.UDPConn, reply <-chan string, chosenBy chan<- *user) {
	for {
		oppName := make([]byte, 1024)
		opponentChan := make(chan *user)
		go func() {
			n, raddr, err := conn.ReadFromUDP(oppName)
			if err != nil {
				if errors.Is(err, net.ErrClosed) {
					return
				}
				log.Panic(err)
			}
			opponentChan <- &user{string(oppName[:n]), raddr}
		}()
		select {
		case opponent := <-opponentChan:
			log.Println("Received Connection Request from", opponent.userName, opponent.ipAddr)
			fmt.Println("Accept Connection Request from", opponent.userName, opponent.ipAddr, "?")
			fmt.Print("Y/n")
			if <-reply == "y" {
				// Tell the player you accept
				_, err := conn.WriteToUDP([]byte("y-"), opponent.ipAddr)
				if err != nil {
					log.Panicln(err)
				}

				// Tell the group you're not available
				gaddr, err := net.ResolveUDPAddr("udp4", groupSoc)
				if err != nil {
					log.Panic(err)
				}
				conn.WriteToUDP([]byte("d-"), gaddr)

				// Play an online chess game with the opponent
				log.Println("Playing with", opponent.userName, "at", opponent.ipAddr)
				chosenBy <- opponent
				return
			} else {
				// Tell the player you reject
				_, err := conn.WriteToUDP([]byte("n-"), opponent.ipAddr)
				if err != nil {
					log.Panicln(err)
				}
				log.Println("Rejected", opponent.userName, "at", opponent.ipAddr)
				continue
			}
		case <-ctx.Done():
			return
		}
	}
}

func printCurrentPlayersList() {
	// Print updated currentPlayers list
	fmt.Printf("Chose a user number (0 - %d)\n", len(currentPlayers)-1)
	for i, u := range currentPlayers {
		fmt.Printf("%d. %v\n", i, u)
	}
}

func listenForAGroupMessage(gconn *net.UDPConn) {
	// Monitor messages sent the group

	buff := make([]byte, 1024)
	// fmt.Println("Listening to the group")
	n, raddr, err := gconn.ReadFromUDP(buff)
	if err != nil {
		if errors.Is(err, net.ErrClosed) {
			return
		}
		log.Panicln(err)
	}

	command := string(buff[:2])
	playerName := string(buff[2:n])
	_, present := ip2Idx[raddr.String()]

	switch command {
	case "p-":
		if !present && playerName != userName {
			log.Printf("Received %s from %s\n", playerName, raddr)
			// Add new available opponent
			ip2Idx[raddr.String()] = len(currentPlayers)
			currentPlayers = append(currentPlayers, &user{playerName, raddr})

			printCurrentPlayersList()
		}

	case "d-":
		if present {
			log.Printf("Removing %s - %s from list\n", playerName, raddr)
			idx := ip2Idx[raddr.String()]
			// Delete opponent that has signified their unavailability
			delete(ip2Idx, raddr.String())
			currentPlayers = append(currentPlayers[:idx], currentPlayers[idx+1:]...)
			// Update indexes in ip2Idx
			for i := idx; i < len(currentPlayers); i++ {
				ip2Idx[currentPlayers[i].ipAddr.String()] = i
			}

			printCurrentPlayersList()
		}
	}
}

func channelInput() {
	var input string
	fmt.Scan(&input)
	input = strings.ToLower(input)
	log.Println("Wrote", input)
	select {
	case replyChan <- input:
		log.Println("Sent reply:", input)
	default:
		if len(currentPlayers) == 0 {
			log.Println("There are no available players currently")
			return
		}
		cIdx, err := strconv.Atoi(input)
		if err != nil {
			log.Println(err)
			return
		}
		if cIdx < 0 || cIdx > len(currentPlayers) {
			log.Printf("Index out of range: choose a number from %d - %d\n", 0, len(currentPlayers)-1)
			return
		}
		chosenIndex = cIdx
		go func ()  {
			log.Printf("Sending currentPlayes[%d]", chosenIndex)
			prospectiveOpponent <- currentPlayers[chosenIndex]
		}()
	}
}

func initiateConnWith(conn *net.UDPConn, prospectiveOpponent *user) {
	_, err := conn.WriteToUDP([]byte("i-"+userName), prospectiveOpponent.ipAddr)
	if err != nil {
		log.Panicln(err)
	}
}

func seekConnection() {
	fmt.Println("Input your username")
	fmt.Scan(&userName)

	conn, err := net.ListenUDP("udp4", nil)
	if err != nil {
		log.Panic(err)
	}
	defer conn.Close()

	gaddr, err := net.ResolveUDPAddr("udp4", groupSoc)
	if err != nil {
		log.Fatalln(err)
	}

	glconn, err := net.ListenMulticastUDP("udp4", nil, gaddr)
	if err != nil {
		log.Panicln(err)
	}
	defer glconn.Close()

	gdconn, err := net.DialUDP("udp4", nil, gaddr)
	if err != nil {
		log.Panicln(err)
	}
	defer gdconn.Close()

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// ip2Idx[gdconn.LocalAddr().String()] = -1

	fmt.Println("caddr", conn.LocalAddr())

	fmt.Println("gdaddr", gdconn.LocalAddr())

	fmt.Println("gaddr", glconn.LocalAddr())

	go func(ctx context.Context) {
		for {
			select {
			case <-ctx.Done():
				return
			default:
				iAmAvailable(conn, gaddr)
				listenForAGroupMessage(glconn)
			}
		}
	}(ctx)

	go func(ctx context.Context) {
		for {
			select {
			case <-ctx.Done():
				return
			default:
				listenForAUnicastMessageAndReply(conn)
			}
		}
	}(ctx)

	for opponent == nil {
		fmt.Println("Channeling Input")
		channelInput()
		select {
		case opponent = <-chosenOpponent:
			fmt.Println("Channeled Opponent", opponent)
		case considering := <- prospectiveOpponent:
			// var considering *user
			// if chosenIndex == -1 {
			// 	log.Println("None chosen")
			// 	continue
			// } else {
			// 	considering = currentPlayers[chosenIndex]
			// }
			log.Println("Recieved", considering)
			initiateConnWith(conn, considering)
			t := time.Tick(30 * time.Second)
			fmt.Println("Waiting For reply from", considering)
			select {
			case opponent = <-chosenOpponent:
				if opponent != nil { // Opponent replied yes (y-)
					fmt.Println("Chosen opponent", chosenIndex, opponent)
				} else { // Opponent replied no (n-)
					fmt.Println("Your connection request was rejected by", considering)
				}
			case <-t:
				fmt.Println("Time up!")
			}
		}
	}
	imUnavailable(conn, gaddr)
	fmt.Println("Chosen:", opponent)
}

func chooseFromPlayerList(conn net.UDPConn, chosenOppIndexStrChan <-chan string, choice chan<- *user) {
	chosenIndexStr := <-chosenOppIndexStrChan
	chosenIndex, err := strconv.Atoi(chosenIndexStr)
	if err != nil {
		log.Panic(err)
	}

	// Request connection with opponent
	_, err = conn.WriteToUDP([]byte("i-"+userName), currentPlayers[chosenIndex].ipAddr)
	if err != nil {
		log.Panicln(err)
	}
	// reply := make([]byte, 1)
	// // Get a reply
	// _, err = conn.Read(reply)
	// if err != nil {
	// 	log.Panic(err)
	// }
	// if reply[0] == 'y' {
	// 	choice <- currentPlayers[chosenIndex]
	// } else {
	// 	log.Println("Rejected by", currentPlayers[chosenIndex].userName, currentPlayers[chosenIndex].ipAddr)
	// }

}

func declareAvailability() {

	gaddr, err := net.ResolveUDPAddr("udp4", groupSoc)
	if err != nil {
		panic(err)
	}

	conn, err := net.ListenUDP("udp4", nil)
	if err != nil {
		panic(err)
	}
	defer conn.Close()

	ip2Idx[conn.LocalAddr().String()] = -1
	fmt.Println("Type a username")
	fmt.Scan(&userName)

	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	for false {
		// Declare availability
		// Passively wait for connection requests
		// Passively Get opponents from the group and Update user list
		// Take user input and
		// 	if it is y/n and there is a connection request do the neccessary
		//	if it is not a y/n but an index send a connection request to the opponent on the user list
		//
	}

	// Declare availability
	go repeatedlyDeclareUsername(ctx, conn, gaddr, userName, 10*time.Second)
	log.Println("Declaring", userName)

	chosenOpponent := make(chan *user)
	choice := make(chan string)

	// Passively wait for opponents' requests and accept or reject them
	go func(ctx context.Context, conn *net.UDPConn, choice chan string) {
		for {
			oppName := make([]byte, 1024)
			n, raddr, err := conn.ReadFromUDP(oppName)
			if err != nil {
				if errors.Is(err, net.ErrClosed) {
					return
				}
				log.Panic(err)
			}

			log.Println("Received Connection Request from", string(oppName[:n]), raddr)
			fmt.Println("Accept Connection Request from", string(oppName[:n]), raddr, "?")
			fmt.Print("Y/n")
			if <-choice == "y" {
				// Tell the player you accept
				_, err = conn.WriteToUDP([]byte("y"), raddr)
				if err != nil {
					log.Panicln(err)
				}
				// Play an online chess game with the opponent
				log.Println("Playing with", string(oppName), "at", raddr)
				opponent := user{string(oppName), raddr}
				chosenOpponent <- &opponent
				return
			} else {
				// Tell the player you reject
				_, err = conn.WriteToUDP([]byte("n"), raddr)
				if err != nil {
					log.Panicln(err)
				}
				log.Println("Rejected", string(oppName), "at", raddr)
				continue
			}
		}
	}(ctx, conn, choice)

	ip2Idx := make(map[string]struct{})
	currentPlayers := []*user{}

	// Update user list everytime a new opponent is available
	go func(ctx context.Context) {
		newAvailableOpponentChan := make(chan *user)
		for {
			// Get an available opponent
			go getNewAvailableOpponent(newAvailableOpponentChan, ip2Idx)
			select {
			case newAvailableOpponent := <-newAvailableOpponentChan:
				// if the opponent has not been added to the list and if the opponent
				// is not the player
				if _, present := ip2Idx[newAvailableOpponent.ipAddr.String()]; !present &&
					newAvailableOpponent.userName != userName {

					ip2Idx[newAvailableOpponent.ipAddr.String()] = struct{}{}
					currentPlayers = append(currentPlayers, newAvailableOpponent)
					fmt.Printf("Chose a user number (0 - %d)\n", len(currentPlayers)-1)
					for i, u := range currentPlayers {
						fmt.Printf("%d. %v\n", i, u)
					}
				}
			case <-ctx.Done():
				return
			}

		}
	}(ctx)

	chosenOppIndexStr := make(chan string)
	// Connect with an opponent from the user list
	go func() {
		chosenIndexStr := <-chosenOppIndexStr
		chosenIndex, err := strconv.Atoi(chosenIndexStr)
		if err != nil {
			log.Panic(err)
		}

		// Request connection with opponent
		_, err = conn.WriteToUDP([]byte(userName), currentPlayers[chosenIndex].ipAddr)
		if err != nil {
			log.Panicln(err)
		}
		reply := make([]byte, 1)
		// Get a reply
		_, err = conn.Read(reply)
		if err != nil {
			log.Panic(err)
		}
		if reply[0] == 'y' {
			chosenOpponent <- currentPlayers[chosenIndex]
		} else {
			log.Println("Rejected by", currentPlayers[chosenIndex].userName, currentPlayers[chosenIndex].ipAddr)
		}
	}()

	takeAndChannelInput := func(choice, chosenOppIndexStr chan<- string) {
		var input string
		_, err := fmt.Scan(&input)
		if err != nil {
			log.Panic(err)
		}
		input = strings.ToLower(input)

		if input == "y" || input == "n" {
			choice <- input
			log.Println("Answer was " + input)
		} else {
			chosenOppIndexStr <- input
			log.Println("Index " + input + " was chosen")
		}
	}

loop:
	for {
		select {
		case opponent := <-chosenOpponent:
			cancel()
			log.Println("Choosen", opponent.userName)
			break loop
		default:
			takeAndChannelInput(choice, chosenOppIndexStr)
		}
	}

	// Play an online chess game with the opponent
}

type user struct {
	userName string
	ipAddr   *net.UDPAddr
}

func udpPing(conn net.UDPConn, raddr *net.UDPAddr) error {
	log.Println("pinging", raddr)
	conn.SetWriteDeadline(time.Now().Add(5 * time.Second))
	_, err := conn.WriteToUDP([]byte("ping"), raddr)
	if err != nil {
		return err
	}

	pong := make([]byte, 4)
	conn.SetReadDeadline(time.Now().Add(5 * time.Second))
	_, err = conn.Read(pong)
	if err != nil && err != io.EOF {
		return err
	}
	// if string(pong) != "pong" {
	// 	return fmt.Errorf("Wrong pong message: %s", pong)
	// }
	log.Println(string(pong))
	return nil
}

func repeatedlyDeclareUsername(ctx context.Context, conn *net.UDPConn, gaddr *net.UDPAddr, userName string, interval time.Duration) {
	_, err := conn.WriteToUDP([]byte(userName), gaddr)
	if err != nil {
		log.Fatalln(err)
	}
	for {
		select {
		case <-ctx.Done():
			log.Println("Stopped Declaring")
			return
		case <-time.Tick(interval):
			_, err := conn.WriteToUDP([]byte("p-"+userName), gaddr)
			if err != nil {
				log.Fatalln(err)
			}
		}
	}
}

func getNewAvailableOpponent(newAvailableOpponentChan chan<- *user, ip2Idx map[string]struct{}) {
	group := "230.1.1.1"
	port := 5000

	gaddr, err := net.ResolveUDPAddr("udp4", fmt.Sprintf("%s:%d", group, port))
	if err != nil {
		log.Fatalln(err)
	}

	conn, err := net.ListenMulticastUDP("udp4", nil, gaddr)
	if err != nil {
		log.Panicln(err)
	}
	defer conn.Close()

	// log.Println("Listening on", conn.LocalAddr())
	buff := make([]byte, 1024)

	for {
		n, raddr, err := conn.ReadFromUDP(buff)
		if err != nil {
			log.Panicln(err)
		}
		command := string(buff[:2])
		if _, present := ip2Idx[raddr.String()]; command == "p-" && !present {
			log.Printf("Received %s from %s\n", string(buff[2:n]), raddr)
			newAvailableOpponentChan <- &user{string(buff[2:n]), raddr}
		}
		if command == "d-" {
			delete(ip2Idx, raddr.String())
		}
	}
}

func main() {
	seekConnection()
}
