name="backup.tar.gz"
mtc_dir="$HOME/.local/share/myioncore"
ip=0
user=$(logname)
# Get arguments
while getopts n:m:i:u: flag
do
	case "${flag}" in
		n) name=${OPTARG};;
    m) mtc_dir=${OPTARG};;
    i) ip=${OPTARG};;
    u) user=${OPTARG};;
    *)
        echo "Flag -${flag} is not recognized. Aborting"
        exit 1 ;;
	esac
done

if [ ! -f "$name" ]; then
    echo "Backup file not found, aborting."
    exit 1
fi

COLOR='\033[92m'
ENDC='\033[0m'

systemctl stop validator
systemctl stop myioncore

echo -e "${COLOR}[1/4]${ENDC} Stopped validator and myioncore"


tmp_dir="/tmp/myioncore/backup"
rm -rf $tmp_dir
mkdir $tmp_dir
tar -xvzf $name -C $tmp_dir

if [ ! -d ${tmp_dir}/db ]; then
    echo "Old version of backup detected"
    mkdir ${tmp_dir}/db
    mv ${tmp_dir}/config.json ${tmp_dir}/db
    mv ${tmp_dir}/keyring ${tmp_dir}/db

fi

rm -rf /var/ion-work/db/keyring

chown -R $user:$user ${tmp_dir}/myioncore
chown -R $user:$user ${tmp_dir}/keys
chown validator:validator ${tmp_dir}/keys
chown -R validator:validator ${tmp_dir}/db

cp -rfp ${tmp_dir}/db /var/ion-work
cp -rfp ${tmp_dir}/keys /var/ion-work
cp -rfpT ${tmp_dir}/myioncore $mtc_dir

chown -R validator:validator /var/ion-work/db/keyring

echo -e "${COLOR}[2/4]${ENDC} Extracted files from archive"

rm -r /var/ion-work/db/dht-*

if [ $ip -ne 0 ]; then
    echo "Replacing IP in node config"
    python3 -c "import json;path='/var/ion-work/db/config.json';f=open(path);d=json.load(f);f.close();d['addrs'][0]['ip']=int($ip);f=open(path, 'w');f.write(json.dumps(d, indent=4));f.close()"
else
    echo "IP is not provided, skipping IP replacement"
fi

echo -e "${COLOR}[3/4]${ENDC} Deleted DHT files"

systemctl start validator
systemctl start myioncore

echo -e "${COLOR}[4/4]${ENDC} Started validator and myioncore"
