# SMAFramework: Urban data integration framework for mobility analysis

## Author: Diego Oliveira <diego@lrc.ic.unicamp.br>

This is an API built as requirement to the author to obtain the master's degree at University of Campinas, Brazil. The code is released currently under the terms of the MIT license described in file `license.txt`.

## Referencing

If you are going to use this lib, please cite the paper:

```
@article{Rodrigues2018,
	abstract = {Sensor networks, connected vehicles and mobile devices are currently used as data collectors in urban environments, data which can be used to better understand the cities' dynamics. Specifically, the study of data-driven solutions to understand the behavior of cities and propose services to enhance the experiences of the citizens in their everyday life has become an active research topic. Many studies in this topic focus on exploring single data sources, and, to tackle this limitation we propose the SMAFramework to collect and integrate urban mobility data from heterogeneous sources. In this work, we propose a methodology that enables the standardization of spatiotemporal annotated data from sources such as Sensor Networks, Vehicular Networks, Social Media and the Web over a single data model (i.e., a Multi-Aspect Graph) and perform different analyses, such as the identification of taxi demand. To show the potential of this framework, we built and assessed a tool to evaluate spatiotemporal correlation of urban data from different sources. Real data collected from social media and a taxi system of the city of New York are used to evaluate this method. The obtained results allowed us to understand some of the applicabilities of the SMAFramework and also provided some insights on how to use it to resolve specific problems when analyzing mobility in urban environments. Using this methodology, we can obtain a better taxi positioning within the city by employing social media data.},
	author = {Rodrigues, Diego O. and Boukerche, Azzedine and Silva, Thiago H. and Loureiro, Antonio A.F. and Villas, Leandro A.},
	doi = {10.1016/J.COMCOM.2018.10.004},
	issn = {0140-3664},
	journal = {Computer Communications},
	month = {oct},
	publisher = {Elsevier},
	title = {{Combining taxi and social media data to explore urban mobility issues}},
	url = {https://www.sciencedirect.com/science/article/pii/S0140366418304225?via{\%}3Dihub},
	year = {2018}
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
