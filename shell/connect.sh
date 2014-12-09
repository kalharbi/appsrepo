echo "Please enter host name:"
read host_name
echo "Please enter your user name:"
read user_name
echo "please enter the port number you wish to open:"
read port_number
ssh -L $port_number:localhost:27017 $user_name@$host_name -N
echo "Connection lost"
