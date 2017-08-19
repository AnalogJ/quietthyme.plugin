FROM analogj/capsulecd:python

RUN echo 'deb http://archive.ubuntu.com/ubuntu trusty main universe restricted' > /etc/apt/sources.list \
    && echo 'deb http://archive.ubuntu.com/ubuntu trusty-updates main universe restricted' >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install --no-install-recommends -y --force-yes build-essential libxcomposite1 libglu1 zip ImageMagick xdg-utils \
    && wget -nv -O- https://raw.githubusercontent.com/kovidgoyal/calibre/master/setup/linux-installer.py | python -c "import sys; main=lambda:sys.stderr.write('Download failed\n'); exec(sys.stdin.read()); main()" \
    && rm -rf /var/lib/apt/lists/*
