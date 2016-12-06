

radio-stations
===============


I'm working on a personal project and I need to assemble the call sign, frequency and antenna locations for every U.S. commercial radio station. Using information from the FCC, this project creates and updates a single Mongodb collection of radio stations.

Python 2.7+ is required to run the code.

**The FCC database**

The Federal Communications Commision uses a MySQL database to store all civilian broadcast station data (commercial, amature, CB, TV, experimental, low-power etc.). The database is backed up to pipe-delimited files and can be found as zip files at ftp://ftp.fcc.gov/pub/Bureaus/MB/Databases/cdbs. The information I use comes from

 - am_ant_sys.zip
 - am_eng_data.zip
 - facility.zip
 - fm_eng_data.zip

**Required Packages**

 - pymongo
 - abc
 - argparse

**Mongodb**
The project assumes that Mongodb is connected to localhost:27017 and requires no credentials to update. If your installation is different, and you don't want to change the code yourself, add a comment and I'll see if I can up the priority on this.

**Running the programs**

 - First make sure that a Mongodb server is running and connected to
   port 27017.
   
 - run the stations.py program against the facility.dat file. Note that this will drop the exisiting collection in the database.

>      python stations.py --help
>     usage: stations.py [-h] [--facility_file FACILITY_FILE]
>                        [--collection COLLECTION] --db_name DBNAME
>     
>     Create station collection from fcc facility data
>     
>     arguments:
>       -h, --help            show this help message and exit
>       --facility_file FACILITY_FILE
>                             path to facility file (i.e. facility.dat) defaults to
>                             facility.dat in current directory
>       --collection COLLECTION
>                             name of collection to create, default is stations.
>                             Drops existing collection if it exists
>       --db_name DBNAME      name of mongodb database, required
>      
>      \>python stations.py --facility_file ..\data\facility.dat --db_name test
>     15267 stations inserted

The next two programs require the stations collection to exist and can be run in any order to populate the antenna array.

 - Run fmant.py against the fm_eng_data.dat file.
 

>\>python fmant.py --help 
> usage: fmant.py [-h] [--eng_file ENG_FILE] [--collection COLLECTION] --db_name
>                 DBNAME
> 
> Update station collection from am_ant_sys and am_eng_data data
> 
> arguments:   -h, --help            show this help message and exit  
> --eng_file ENG_FILE   --collection COLLECTION
>                         name of collection to create, default is stations   --db_name DBNAME
> 

- Run amant.py against the am_ant_sys.dat and am_eng_data.dat files

> \>python amant.py --help 
> usage: amant.py [-h] [--ant_file ANT_FILE] [--eng_file ENG_FILE] --db_name
>                 DBNAME
> 
> Update station collection from am_ant_sys and am_eng_data data
> 
> optional arguments:   -h, --help           show this help message and
> exit   --ant_file ANT_FILE   --eng_file ENG_FILE   --db_name DBNAME
> 
 
>Written with [StackEdit](https://stackedit.io/).