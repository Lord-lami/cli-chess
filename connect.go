package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"net"
	"strconv"
	"strings"
	"time"
)

const (
	groupSoc string = "230.1.1.1:5000"
)

// userName is the userName of this user.
var userName string

// ip2Idx maps IP address strings
// to their index in [currentPlayers].
var ip2Idx map[string]int = make(map[string]int)

type user struct {
	userName string
	ipAddr   *net.UDPAddr
}

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

// waitDuration is the duration in seconds
// that a connection request will wait for
// before timing out.
var waitDuration int = 30

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
	log.Println("I'm Unavailable")
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

	isReplyFromChosenPlayer := chosenIndex >= 0 &&
		chosenIndex < len(currentPlayers) &&
		raddr.String() == currentPlayers[chosenIndex].ipAddr.String()
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

		t := time.NewTimer(time.Duration(waitDuration) * time.Second)

		select {
		// Inputted reply is sent on reply channel
		case reply := <-replyChan:
			if "y" == reply {
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
		// Exit in case of a time out
		case <-t.C:
			fmt.Println("Time's up!")
		}
	}
}

func printCurrentPlayersList() {
	// Print updated currentPlayers list
	if len(currentPlayers) > 0 {
		fmt.Printf("Chose a user number (0 - %d)\n", len(currentPlayers)-1)
		for i, u := range currentPlayers {
			fmt.Printf("%d. %v\n", i, u)
		}
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
		log.Printf("%s is unavailable\n", playerName)
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
		go func() {
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
		case considering := <-prospectiveOpponent:
			// var considering *user
			// if chosenIndex == -1 {
			// 	log.Println("None chosen")
			// 	continue
			// } else {
			// 	considering = currentPlayers[chosenIndex]
			// }
			log.Println("Recieved", considering)
			initiateConnWith(conn, considering)
			fmt.Println("Waiting For reply from", considering)
			t := time.NewTimer(time.Duration(waitDuration) * time.Second)
			select {
			case opponent = <-chosenOpponent:
				if opponent != nil { // Opponent replied yes (y-)
					fmt.Println("Chosen opponent", chosenIndex, opponent)
				} else { // Opponent replied no (n-)
					fmt.Println("Your connection request was rejected by", considering)
				}
			case <-t.C:
				fmt.Println("Time's up!")
			}
		}
	}
	cancel()
	for range 4 {
		imUnavailable(conn, gaddr)
	}

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


func main() {
	seekConnection()
}
