.PHONY: build-dev enter-dev config

all:
	docker-compose build

build-dev:
	docker-compose -f docker-compose-dev.yml build --build-arg UID=`id -u` \
						       --build-arg GID=`id -g`

enter-dev:
	docker-compose -f docker-compose-dev.yml run --rm --user=`id -u` --use-aliases voicetalk ash

config:
	# Copy VoiceTalk sample configuration file
	docker run --name tmp-voicetalk -d voicetalk
	docker cp tmp-voicetalk:/voicetalk/voicetalk.ini.sample ./voicetalk/voicetalk.ini.sample
	docker cp tmp-voicetalk:/voicetalk/device.json.sample ./voicetalk/device.json.sample
	docker rm -f tmp-voicetalk
	# Copy Nginx sample configuration file
	docker run --name tmp-nginx -d nginx
	docker cp tmp-nginx:/etc/nginx/nginx.conf ./nginx/nginx.conf.sample
	docker rm -f tmp-nginx
