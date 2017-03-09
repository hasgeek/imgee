FROM ubuntu:xenial

RUN apt-get purge -y python.*

RUN apt-get -y update && apt-get install -y apt-utils build-essential git curl python2.7 python2.7-dev python-setuptools software-properties-common python-software-properties python-pip libxml2 libxslt1.1 libxml2-dev libxslt1-dev libffi-dev imagemagick webp inkscape unzip liblcms2-dev python-imaging python-reportlab libjpeg-dev libpng-dev libfreetype6-dev librsvg2-dev ghostscript libssl-dev postgresql-server-dev-9.5

RUN pip install --upgrade pip

RUN pip install https://github.com/sk1project/uniconvertor/archive/master.zip

COPY requirements.txt /opt/imgee/requirements.txt
WORKDIR /opt/imgee
RUN pip install -r requirements.txt

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 25
EXPOSE 4500
EXPOSE 5432

COPY . /opt/imgee

CMD ["uwsgi", "-i", "uwsgi.ini"]
