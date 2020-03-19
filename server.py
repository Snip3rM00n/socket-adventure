import socket


class Server(object):
    """
    An adventure game socket server
    
    An instance's methods share the following variables:
    
    * self.socket: a "bound" server socket, as produced by socket.bind()
    * self.client_connection: a "connection" socket as produced by socket.accept()
    * self.input_buffer: a string that has been read from the connected client and
      has yet to be acted upon.
    * self.output_buffer: a string that should be sent to the connected client; for
      testing purposes this string should NOT end in a newline character. When
      writing to the output_buffer, DON'T concatenate: just overwrite.
    * self.done: A boolean, False until the client is ready to disconnect
    * self.room: one of 0, 1, 2, 3. This signifies which "room" the client is in,
      according to the following map:
      
                                     3                      N
                                     |                      ^
                                 1 - 0 - 2                  |
                                 
    When a client connects, they are greeted with a welcome message. And then they can
    move through the connected rooms. For example, on connection:
    
    OK! Welcome to Realms of Venture! This room has brown wall paper!  (S)
    move north                                                         (C)
    OK! This room has white wallpaper.                                 (S)
    say Hello? Is anyone here?                                         (C)
    OK! You say, "Hello? Is anyone here?"                              (S)
    move south                                                         (C)
    OK! This room has brown wall paper!                                (S)
    move west                                                          (C)
    OK! This room has a green floor!                                   (S)
    quit                                                               (C)
    OK! Goodbye!                                                       (S)
    
    Note that we've annotated server and client messages with *(S)* and *(C)*, but
    these won't actually appear in server/client communication. Also, you'll be
    free to develop any room descriptions you like: the only requirement is that
    each room have a unique description.
    """

    game_name = "Explore the Andromeda Timecraft (ATC) Serendipity"

    def __init__(self, port=50000):
        self.input_buffer = ""
        self.output_buffer = ""
        self.done = False
        self.socket = None
        self.client_connection = None
        self.port = port

        self.room = 0

    def connect(self):
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)

        address = ('127.0.0.1', self.port)
        self.socket.bind(address)
        self.socket.listen(1)

        self.client_connection, address = self.socket.accept()

    def room_description(self, room_number):
        """
        For any room_number in 0, 1, 2, 3, return a string that "describes" that
        room.

                                     3                      N
                                     |                      ^
                                 1 - 0 - 2                  |

        Ex: `self.room_number(1)` yields "Brown wallpaper covers the walls, bathing
        the room in warm light reflected from the half-drawn curtains."

        :param room_number: int
        :return: str
        """
        craft_plaque = str("\n\n\"ATC Serendipity (KTIME01)"
                           "\n\n'The universe, in its infinite perfection, is "
                           "merely an unlikely series of Serendipities.' - "
                           "Stella Starchelle (The Mother of Interstellar "
                           "Flight), 0 SFE (Space Faring Era)"
                           "\n\nThis Timecraft is an Ekiya Glide Company 256 "
                           "Glyde Gx 2350 Temporal Edition commissioned on "
                           "03/17/32915 SFE by the AHC Department of Temporal Integrity:"
                           "\n\nKima Amber Metoyo (Temporal Operative)"
                           "\nAstra Jayne Matsume (Temporal Analyst)"
                           "\nDelilah Quincy Matsuka (Temporal Developer)\"")

        rooms = {0: "You are at the temporal developer console.  The curved glass screen displays the tmpOrl IDE and the code to fold the time craft through the fourth dimension (time).",
                 1: "You are at the port side of the timecraft.  The only thing here is a small control panel for opening the glass windshield of the timecraft.  The controls are greyed out with the word 'Unauthorized' overlayed on them.",
                 2: f"You are at the starbord side of the timecraft.  There is a plaque on the wall that reads: {craft_plaque}",
                 3: "You are at the front of the timecraft.  The temporal operative and temporal analyst would sit here to guide the craft.  On the dashboard, the chronotonium temporal filament sparkles in a dazzling array of colors underneith a dome of glass."}

        return rooms.get(room_number)

    def greet(self):
        """
        Welcome a client to the game.
        
        Puts a welcome message and the description of the client's current room into
        the output buffer.
        
        :return: None 
        """
        self.output_buffer = "Welcome to {}! {}".format(
            self.game_name,
            self.room_description(self.room)
        )

    def get_input(self):
        """
        Retrieve input from the client_connection. All messages from the client
        should end in a newline character: '\n'.
        
        This is a BLOCKING call. It should not return until there is some input from
        the client to receive.
         
        :return: None 
        """
        msg = b""

        while b'\n' not in msg:
            msg += self.client_connection.recv(16)
        
        self.input_buffer = msg.decode().strip()

    def move(self, argument):
        """
        Moves the client from one room to another.
        
        Examines the argument, which should be one of:
        
        * "north"
        * "south"
        * "east"
        * "west"

        "Moves" the client into a new room by adjusting self.room to reflect the
        number of the room that the client has moved into.
        
        Puts the room description (see `self.room_description`) for the new room
        into "self.output_buffer".
        
        :param argument: str
        :return: None
        """
        argument = argument.lower()
        room = None

        if argument == "north" and self.room == 0:
            self.room = 3
        elif argument == "south" and self.room == 3:
            self.room = 0
        elif argument == "east" and self.room == 0:
            self.room = 1
        elif argument == "east" and self.room == 2:
            self.room = 0
        elif argument == "west" and self.room == 0:
            self.room = 2
        elif argument == "west" and self.room == 1:
                self.room = 0
        else:
            room = f"Bad! You cannot move in that direction."
        
        room = self.room_description(self.room) if room is None else room

        # This should be impossible to encounter, however handle the case to
        # prevent undesired crashing.
        if not room:
            room = str("You have some how entered an invalid state and the "
                       "timeline is collapsing!  You feel an unnerving lurch "
                       "as you are torn from the colapsing timeline and "
                       "returned to a stable timeline.")
            self.room = 0

        self.output_buffer = room

    def say(self, argument):
        """
        Lets the client speak by putting their utterance into the output buffer.
        
        For example:
        `self.say("Is there anybody here?")`
        would put
        `You say, "Is there anybody here?"`
        into the output buffer.
        
        :param argument: str
        :return: None
        """

        self.output_buffer = f"You say, \"{argument}\""

    def quit(self, argument):
        """
        Quits the client from the server.
        
        Turns `self.done` to True and puts "Goodbye!" onto the output buffer.
        
        Ignore the argument.
        
        :param argument: str
        :return: None
        """

        self.done = True
        self.output_buffer = "Goodbye!"

    def route(self):
        """
        Examines `self.input_buffer` to perform the correct action (move, quit, or
        say) on behalf of the client.
        
        For example, if the input buffer contains "say Is anybody here?" then `route`
        should invoke `self.say("Is anybody here?")`. If the input buffer contains
        "move north", then `route` should invoke `self.move("north")`.
        
        :return: None
        """
        command = self.input_buffer.split(' ')[0].lower()
        action = " ".join(self.input_buffer.split(' ')[1:])
        
        functions = {"quit": self.quit,
                     "say": self.say,
                     "move": self.move}

        function = functions.get(command)

        if function:
            function(action)
        else:
            self.output_buffer = "Bad! You can either move, say, or quit."

    def push_output(self):
        """
        Sends the contents of the output buffer to the client.
        
        This method should prepend "OK! " to the output and append "\n" before
        sending it.
        
        :return: None 
        """

        if self.output_buffer.startswith("Bad!"):
            self.client_connection.sendall(f"{self.output_buffer} \n".encode())
        else:
            self.client_connection.sendall(f"OK! {self.output_buffer} \n".encode())

    def serve(self):
        self.connect()
        self.greet()
        self.push_output()

        while not self.done:
            self.get_input()
            self.route()
            self.push_output()

        self.client_connection.close()
        self.socket.close()
