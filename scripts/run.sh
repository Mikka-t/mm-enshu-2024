docker-compose restart

echo "access to your web page"
ip="`ip a | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1 | grep 10.0`"
echo "http://$ip:8000/"