docker-compose up --build -d --force-recreate

# Get the IP address
IP_ADDR=$(hostname -I | awk '{print $1}')

# Construct the URL
URL="http://$IP_ADDR:8000/"

# Echo the URL
echo "Access the application at: $URL"