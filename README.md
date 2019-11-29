# itsonedb-api

In order to grant [**ITSoneDB**](http://itsonedb.cloud.ba.infn.it) systematic flow into new ENA service a restful API has been created, i.e an __Application Program Interface__ that uses `http` for requests.  
In particular only `GET` requests are allowed. The new API is based on [Flask](http://flask.pocoo.org/docs/1.0/) and it is currently available at the following web address:
```
http://itsonedb-api.cloud.ba.infn.it:8080
```
It is currently based on **ITSoneDB** release 1.131 and queries are supported only by accession number.  
For instance, it is possible to query **ITSoneDB** using `curl`: 
```
curl http://itsonedb-api.cloud.ba.infn.it:8080/api/accession/<ACCESSION_NUMBER>
```
receiving the sequences as output.

Usage
-----

The API can be exploited through `curl`, querying **ITSoneDB** by Accession Number.  
For instance:
```
http://itsonedb-api.cloud.ba.infn.it:8080/api/accession/AY582110
```
while the `curl` is:
```
$ curl -v http://itsonedb-api.cloud.ba.infn.it:8080/api/accession/AY582110
*   Trying 90.147.75.12...
* TCP_NODELAY set
* Connected to itsonedb-api.cloud.ba.infn.it (90.147.75.12) port 8080 (#0)
> GET /api/accession/AY582110 HTTP/1.1
> Host: itsonedb-api.cloud.ba.infn.it:8080
> User-Agent: curl/7.54.0
> Accept: */*
>
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Content-Type: application/json
< Content-Length: 501
< Server: Werkzeug/0.15.2 Python/2.7.12
< Date: Mon, 20 May 2019 15:24:38 GMT
<
{"data": [">AY582110_ITS1_ENA|ITS1 localized by ENA annotation, 399 bp length;", "ttttttgcgcgagccaagacatccattgctgaaaatttaaaataacattatagtttaggaagcaatctgaaagcacatcg", "agagagatgcagaaagatacaatctttcactctctctcaaatgttcctcagatttgttgtttgaaataacggtgtgggaa", "aaaagaatgcacactgaagaaactcctggaaatcagtatcccaacagagacacgaatttccagaaattgagccccttcgc", "tgtgcacccccggatacctgcactggcttccaatattggaagcagcgcaggatatccaacatgaagaaggcaataatacc", "tttcgatactatcacgcttcttgaatgcaaatctctccaatggagagagatgcaaactcatgttttgcttgggattcaa"]}
* Closing connection 0
```

Installation
------------
We recommend [**Ubuntu**](https://ubuntu.com) as Operative System.

Install dependencies:
```
# apt-get install build-essential python-dev
# apt-get install libmysqlclient-dev
```

Clone this repository.

Craete python virtual environment and name it .venv:
```
$ cd /home/ubuntu/itsonedb-api
$ virtualenv .venv
$ cd .venv
$ . .venv/bin/activate
$ pip install -r requirements.txt
```

Install gunicorn systemd unit file:
```
# cp gunicorn/itsonedb-api.service /etc/systemd/system/
# systemctl enable itsonedb-api
# systemctl start itsonedb-api
```

Setup nginx web server:
```
# apt-get install nginx
# cp nginx/itsonedb-api /etc/nginx/sites-available
# ln -s /etc/nginx/sites-available/itsonedb-api /etc/nginx/sites-enabled/
# systemctl restart nginx
```

Finally the `itsonedb-api` is available on 8080 port.

Citation
--------
The already published papers regard **ITSoneDB** and a manuscript regarding the associated services, like the `itsonedb-api`, is currently in preparation.  
Please refer to:  
1. [Santamaria, M., Fosso, B., Consiglio, A., De Caro, G., Grillo, G., Licciulli, F., Liuni, S., Marzano, M., Alonso-Alemany, D., Valiente, G., Pesole, G., 2012. ***Reference databases for taxonomic assignment in metagenomics.*** *Briefings in bioinformatics* 13 %6, 682–95 % & . https://doi.org/10.1093/bib/bbs036](https://doi.org/10.1093/bib/bbs036)  
2. [Santamaria, M., Fosso, B., Licciulli, F., Balech, B., Larini, I., Grillo, G., De Caro, G., Liuni, S., Pesole, G., 2018. ***ITSoneDB: a comprehensive collection of eukaryotic ribosomal RNA Internal Transcribed Spacer 1 (ITS1) sequences.*** *Nucleic Acids Res* 46, D127–D132. https://doi.org/10.1093/nar/gkx855](https://doi.org/10.1093/nar/gkx855)
