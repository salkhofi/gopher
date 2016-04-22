
import sys #system main library
import socket #sockets library
import os #os library to carry out networking requests.
import string #string library

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connection Parameters
SEL      = 'ABC' #Selector is the stream connection to the port
HOST     = 'localhost' #hostname
PORT     = 8070  #portNumber

s.bind(('', PORT))
s.listen(5)


#  the files types that the server is going to support
TEXTFILE  = '0'
MENU      = '1'
CSO       = '2'
ERROR     = '3'
SEARCH    = '4'
TELNET    = '5'
BINARY    = '6'
REDUNDANT = '+'

#storing all our file types in a dictionary
type_dictionary = {'0': '<TEXT>', '1': '<DIR>', '2': '<CSO>', '3': '<ERROR>', \
        '4': '<BINHEX>', '5': '<DOS>', '6': '<UUENCODE>', '7': '<SEARCH>', \
        '8': '<TELNET>', '9': '<BINARY>', '+': '<REDUNDANT>', 's': '<SOUND>'}

CRLF = '\r\n'
TAB = '\t'

# Open Socket Connection and Handle Error
# If port is not open:Open Port.
# connect_socket socket on the port and open selector for DATA STREAM
# Return server object
def connect_socket(myHost, myPort):
    if not myPort:
        myPort = PORT
    elif type(myPort) == type(''): 
        myPort = string.atoi(myPort) # Convert port to integer value
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Open socket
    s.connect((myHost, myPort));
    print '(Server Running)'
    return s

# Selector starts working and wait for text file
def selector_start(mySelector, myHost, myPort):
    c = connect_socket(myHost, myPort)
    c.send(mySelector + CRLF)
    c.shutdown(socket.SHUT_RDWR)
    return c.makefile('r')

# Display Menu as a list of entries
# Open data Stream and start fetching data
# Handle error cases when file has ended etc.
# In the end,append all data read into one value and close the data stream.
def menu_display(mySelector, myHost, myPort):
    d_file = selector_start(mySelector, myHost, myPort)#this is data file.
    list = []
    while 1:
        file_data_stream = d_file.readline()
        if not file_data_stream:
            for key, value in type_dictionary.iteritems():
                temp = [key,value]
                list.append(temp)
            break
        if file_data_stream[-2:] == CRLF:
            file_data_stream = file_data_stream[:-2]
        elif file_data_stream[-1:] in CRLF:
            file_data_stream = file_data_stream[:-1]
        if file_data_stream == '.':
            break
        if not file_data_stream:
            print '(Empty Line Occured /Server\)'
            continue
        typechar = file_data_stream[0] #convert data stream
        parts = string.splitfields(file_data_stream[1:], TAB) #seperate tabs
        if len(parts) < 4:
            print '(Corrupted Line /Server\: %r)' % (file_data_stream,)
            continue
        if len(parts) > 4:
            print '(Extra Data /Server\: %r)' % (parts[4:],)
        parts.insert(0, typechar)#insert word fetched to list
        list.append(parts) #append all words
    d_file.close() #close data stream
    return list

# Process Binary file in Blocks
def fetch_binary(mySelector, myHost, myPort):
    d_file = selector_start(mySelector, myHost, myPort)
    data = d_file.read() 
    d_file.close()
    return data

# Get the data block fetched and pass it for processing
def process_binary(mySelector, myHost, myPort, func, blocksize):
    f = selector_start(mySelector, myHost, myPort)
    while 1: 
        data = f.read(blocksize)
        if not data: 
            break
        func(data)


# Start fetching file from the server and handle any error
# Start reading file data if nothing found alert user 
# clear all the whitespaces and other invalid data from stream

def fetch_text_file(mySelector, myHost, myPort):
    list = [] 
    process_textfile(mySelector, myHost, myPort, list.append) 
    return list 

# Process a text file and pass each file_data_stream to a function
def process_textfile(mySelector, myHost, myPort, func):
    d_file = selector_start(mySelector, myHost, myPort)
    while 1:
        file_data_stream = d_file.readline()
        if not file_data_stream:
            break
        if file_data_stream[-2:] == CRLF:
            file_data_stream = file_data_stream[:-2]
        elif file_data_stream[-1:] in CRLF:
            file_data_stream = file_data_stream[:-1]
        if file_data_stream == '.':
            break
        if file_data_stream[:2] == '..':
            file_data_stream = file_data_stream[1:]
        func(file_data_stream)
    d_file.close()


# Explorer to browse through data and make selection
# explorer has default arguments
def explorer(*args):
    mySelector = SEL
    myHost = HOST
    myPort = PORT
    # Validate number of arguments that explorer needs and handle error
    n = len(args)
    if n > 0 and args[0]:
        mySelector = args[0]
    if n > 1 and args[1]:
        myHost = args[1]
    if n > 2 and args[2]:
        myPort = args[2]
    if n > 3:
        raise RuntimeError, 'Too many arguments' 
    try:
        explore_menu(mySelector, myHost, myPort) 
    except socket.error, msg:
        print 'Socket error:', msg
        sys.exit(1)
    except KeyboardInterrupt: #If keyboard key is pressed.Exit
        print '\n[Finished]'

# Menu 
# and
# Handle error in case of any strange behaviour of the server
def explore_menu(mySelector, myHost, myPort):
    list = menu_display(mySelector, myHost, myPort)
    while 1:
        print '----- GOPHERS Server MENU -----' #Dislay Menu
        print 'Selector:', repr(mySelector)
        print 'Host:', myHost, ' Port:', myPort
        print
        for i in range(len(list)): #Range of types is 0-6
        
            item = list[i]
            typechar, description = item[0], item[1]
            print string.rjust(repr(i+1), 3) + ':', description,
            if type_dictionary.has_key(typechar):
                print type_dictionary[typechar]
            else: #if type is not matched
                print '<TYPE=' + repr(typechar) + '>'


        print
        for key, value in type_dictionary.iteritems():
            temp = [key,value]
            list.append(temp) 
        while 1:
            try: #user choice of function
                str = raw_input('Choice [CR == up a level]:')
            except EOFError:
                print
                for key, value in type_dictionary.iteritems():
                  temp = [key,value]
                  list.append(temp)
                return
            if not str:
                return
            try: #handle choice related errors
                choice = string.atoi(str)
            except string.atoi_error:
                print 'Choice must be a number; try again:'
                continue
            if not 0 < choice <= len(list):
                print 'Choice is out of range; try again:'
                continue
            print ('Operation Successfull')
            print ('Continuing.use ctrl-c to break')    
            break
     
        typechar = 0
        i_selector = SEL
        i_host = HOST
        i_port = PORT 
        if typeexplorer.has_key(typechar):
            explorerfunc = typeexplorer[typechar] 
            try:
                explorerfunc(i_selector, i_host, i_port)
            except (IOError, socket.error):
                print '***', sys.exc_type, ':', sys.exc_value
        else:
            print 
            #print 'Unsupported object type' #object type is not supported error


# Text file 
def explore_textfile(mySelector, myHost, myPort):
    x = None #File stream
    try:
        p = os.popen('${PAGER-more}', 'w') #Open file in write mode using pager stream option
        x = SaveLines(p) #Save data in file
        process_textfile(mySelector, myHost, myPort, x.writeln) # Call Process text file in order to do something with file data 
    except IOError, msg:
        print 'I/OError:', msg
    if x:
        x.close()
    f = open_savefile()
    if not f:
        return
    x = SaveLines(f)
    try:
        process_textfile(mySelector, myHost, myPort, x.writeln) #File realted errors
        print 'Completed.'
    except IOError, msg:
        print 'I/OError:', msg
    x.close()

# explore a search indeX
def explore_search(mySelector, myHost, myPort):
    while 1: # Display Gophers search menu
        print '----- GOPHERS SERVER SEARCH -----'
        print 'Selector:', repr(mySelector)
        print 'Host:', myHost, ' Port:', myPort
        print
        try:
            query = raw_input('Query [CR == up a level]: ') #Get user choice
        except EOFError:
            print
            break
        query = string.strip(query) 
        if not query:
            break
        if '\t' in query:
            print 'Remove tabs from query and try again!!'
            continue
        explore_menu(mySelector + TAB + query, myHost, myPort) #Explore menu when done


# Explore and save Binary File
def explore_binary(mySelector, myHost, myPort):
    f = open_savefile()
    if not f:
        return
    x = SaveWithProgress(f)
    process_binary(mySelector, myHost, myPort, x.write, 8*1024)
    x.close()


# Process telnet information.Make connection.
def explore_telnet(mySelector, myHost, myPort):
    if mySelector:
        print 'Log in as', repr(mySelector)
    if type(myPort) <> type(''):
        myPort = repr(myPort)
    sts = os.system('set -x; exec telnet ' + myHost + ' ' + myPort) #telnet connection string
    if sts:
        print 'Exit status:', sts


# Dictionary type mapping for the file types 
typeexplorer = {'0': explore_textfile, '1': explore_menu, \
        '4': explore_search, '5': explore_telnet, '6': explore_binary}

# Class for appending a newline to each file_data_stream
class SaveLines:
    def __init__(self, f):
        self.f = f
    def writeln(self, file_data_stream):
        self.f.write(file_data_stream + '\n')
    def close(self):
        sts = self.f.close()
        if sts:
            print 'Exit status:', sts

# Class used to save data while showing progress
class SaveWithProgress:
    def __init__(self, f):
        self.f = f
    def write(self, data):
        sys.stdout.write('#') #write data to standard output
        sys.stdout.flush() #flush output
        self.f.write(data)
    def close(self):
        print
        sts = self.f.close()
        if sts:
            print 'Exit status:', sts 

# Ask for and open a save file, or return None if not to save
def open_savefile():
    try:
        savefile = raw_input( \
    'Save data as file [CR == don\'t save; |pipeline or ~user/... OK]: ')
    except EOFError:
        print
        return None
    savefile = string.strip(savefile) #save file after removing CRLF
    if not savefile:
        return None
    if savefile[0] == '|':
        cmd = string.strip(savefile[1:])
        try:
            p = os.popen(cmd, 'w') #Open data pipe in write mode
        except IOError, msg:
            print repr(cmd), ':', msg
            return None
        print 'Piping through', repr(cmd), '...'
        return p
    if savefile[0] == '~':
        savefile = os.path.expanduser(savefile)
    try:
        f = open(savefile, 'w')
    except IOError, msg:
        print repr(savefile), ':', msg
        return None
    print 'Saving to', repr(savefile), '...' # save the file when everything is done
    return f


# Test program
def test():
    if sys.argv[4:]:
        print 'usage: gopher [ [Selector] Host [Port] ]'
        sys.exit(2)
    elif sys.argv[3:]:
        explorer(sys.argv[1], sys.argv[2], sys.argv[3]) 
    elif sys.argv[2:]:
        # Handle error cases for arguments.If lesser or more arguments are provided
        try: 
            myPort = string.atoi(sys.argv[2])
            mySelector = ''
            myHost = sys.argv[1]
        except string.atoi_error:
            mySelector = sys.argv[1]
            myHost = sys.argv[2]
            myPort = ''
        explorer(mySelector, myHost, myPort) #call explorer to start program
    elif sys.argv[1:]:
        explorer('', sys.argv[1]) 
    else:
        explorer() #If nothing mentioned just start default explorer

# Call test
test()