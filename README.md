# Creative Name Goes here


## Steps

### Step 1:
Setup nginx with the config file provided 

### Step 2: Wildcard DNS to the server
Can be done in namecheap

### Step 3: Get a valid SSL cert
```bash
sudo certbot certonly --preferred-challenges dns -d berinternal.com -d '*.berinternal.com'
```
### Step 4: Run the webserver
```bash
python main.py
```
Add additional service worker routes and service worker files for more domains
