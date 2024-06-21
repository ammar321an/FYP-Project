#!/bin/bash
# Add an initial delay to ensure all services are up
sleep 10  # Delay for 30 seconds
# Function to check if the Raspberry Pi is connected to the "iPhone" Wi-Fi network
check_wifi_connection() {
    local wifi_name="iPhone"
    local connected_ssid=$(iwgetid -r)
    echo "Connected SSID: $connected_ssid"  # Log the connected SSID
    if [ "$connected_ssid" == "$wifi_name" ]; then
        return 0  # Connected to the desired Wi-Fi network
    else
        return 1  # Not connected to the desired Wi-Fi network
    fi
}
# Function to get the IP address
get_ip_address() {
    local ip_address
    # Use hostname command to get the IP address(es) and select the first one
    ip_address=$(hostname -I | awk '{print $1}')
    echo "$ip_address"  # Log the IP address
}
# Log start of script
echo "Script started" >> /home/ammarPi/log.txt
# Display "Finding ..." on the LCD
echo "Displaying 'Finding ...' on the LCD"  # Log display message
python /home/ammarPi/update_lcd.py "Finding ..." ""
sleep 4  # Delay for 4 seconds
# Wait for the Wi-Fi connection
attempts=0
max_attempts=3  # Maximum number of attempts to connect
while true; do
    check_wifi_connection
    if [ $? -eq 0 ]; then
        connected_ssid=$(iwgetid -r)
        echo "Connected to $connected_ssid"  # Log Wi-Fi connection
        echo "Connected to $connected_ssid" >> /home/ammarPi/log.txt
        break  # Connected to the desired Wi-Fi network
    else
        ((attempts++))
        if [ $attempts -ge $max_attempts ]; then
            echo "Max attempts reached, not connected to Wi-Fi"  # Log failure
            echo "Max attempts reached, not connected to Wi-Fi" >> /home/ammarPi/log.txt
            # Exit the script after maximum attempts
            break
        else
            echo "Attempt $attempts: Searching for Wi-Fi network $wifi_name"  # Log attempts
            echo "Attempt $attempts: Searching for Wi-Fi network $wifi_name" >> /home/ammarPi/log.txt
            python /home/ammarPi/update_lcd.py "Searching for" "$wifi_name"
            sleep 2  # Delay for 2 seconds
        fi
    fi
    sleep 3  # Wait for 3 seconds before checking again
done
# Display "Connecting..." with SSID on the LCD
echo "Displaying 'Connecting...' with SSID $connected_ssid on the LCD"  # Log display message
python /home/ammarPi/update_lcd.py "Connecting..." "$connected_ssid"
sleep 2  # Delay for 2 seconds
# Simulate the connection attempt delay
sleep 3
# Get the IP address
ip_address=$(get_ip_address)
# Display "Connected to" with IP address on the LCD
echo "Displaying 'Connected to' with IP address $ip_address on the LCD"  # Log display message
python /home/ammarPi/update_lcd.py "Connected to IP:" "$ip_address/5000"
sleep 2  # Delay for 2 seconds
# Run the Python script
python /home/ammarPi/update_lcd.py "Robot is :::" "READY"
# Log end of script
echo "Script finished" >> /home/ammarPi/log.txt