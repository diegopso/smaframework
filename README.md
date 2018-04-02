# SMAFramework: Urban data integration framework for mobility analysis

## Author: Diego Oliveira <diego@lrc.ic.unicamp.br>

This is an API built as requirement to the author to obtain the master's degree at University of Campinas, Brazil. The code is released currently under the terms of the MIT license described in file `license.txt`.

## Referencing

If you are going to use this lib, please cite the paper:

```
@inproceedings{Rodrigues:2017:SUD:3127540.3127569,
	address = {New York, NY, USA},
	author = {Rodrigues, Diego O and Boukerche, Azzedine and Silva, Thiago H and Loureiro, Antonio A F and Villas, Leandro A},
	booktitle = {Proceedings of the 20th ACM International Conference on Modelling, Analysis and Simulation of Wireless and Mobile Systems},
	doi = {10.1145/3127540.3127569},
	isbn = {978-1-4503-5162-1},
	keywords = {big data,mobility analysis,smart cities,urban data},
	pages = {227--236},
	publisher = {ACM},
	series = {MSWiM '17},
	title = {{SMAFramework: Urban Data Integration Framework for Mobility Analysis in Smart Cities}},
	url = {http://doi.acm.org/10.1145/3127540.3127569},
	year = {2017}
}

```

## Setup Python VENV

```
$ sudo apt-get update
$ sudo apt-get -y upgrade
$ sudo apt-get install -y python3-pip build-essential libssl-dev libffi-dev python-dev python3-venv libgeos-dev libblas-dev liblapack-dev gfortran
$ python3 -m venv smaframework
$ source smaframework/bin/activate
$ mkdir smaframework/src
$ git clone https://bitbucket.org/smaframework/smaframework.git smaframework/src
$ cd smaframework/src && pip install .
$ mkdir data
$ mkdir data/results/
$ cp .env.sample .env & nano .env
```

## Examples 

There are examples in the `/examples/` folder, they run with sample data generated randomly or based in a public dataset. They might run and save results to the `/data/` and `/data/results/` forlders without complications after the configuration of the needed keys in the environment file. To configure the environment, copy `.env.example` to `.env` and set needded keys -- you may check the example code to see what are the needed keys.

## TODO

 * Prepare documentation of the lib;
 * Prepare tests to facilitate contributions.
