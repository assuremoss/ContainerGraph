[
    {
        "Id": "sha256:ea335eea17ab984571cd4a3bcf90a0413773b559c75ef4cda07d0ce952b00291",
        "RepoTags": [
            "nginx:latest"
        ],
        "RepoDigests": [
            "nginx@sha256:097c3a0913d7e3a5b01b6c685a60c03632fc7a2b50bc8e35bcaa3691d788226e"
        ],
        "Parent": "",
        "Comment": "",
        "Created": "2021-11-17T10:38:14.652464384Z",
        "Container": "8a038ff17987cf87d4b7d7e2c80cb83bd2474d66e2dd0719e2b4f7de2ad6d853",
        "ContainerConfig": {
            "Hostname": "8a038ff17987",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "ExposedPorts": {
                "80/tcp": {}
            },
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "NGINX_VERSION=1.21.4",
                "NJS_VERSION=0.7.0",
                "PKG_RELEASE=1~bullseye"
            ],
            "Cmd": [
                "/bin/sh",
                "-c",
                "#(nop) ",
                "CMD [\"nginx\" \"-g\" \"daemon off;\"]"
            ],
            "Image": "sha256:2fb4060b053a39040c51ff7eadd30325de2c76650fc50aa42839070e16e8bdcb",
            "Volumes": null,
            "WorkingDir": "",
            "Entrypoint": [
                "/docker-entrypoint.sh"
            ],
            "OnBuild": null,
            "Labels": {
                "maintainer": "NGINX Docker Maintainers <docker-maint@nginx.com>"
            },
            "StopSignal": "SIGQUIT"
        },
        "DockerVersion": "20.10.7",
        "Author": "",
        "Config": {
            "Hostname": "",
            "Domainname": "",
            "User": "",
            "AttachStdin": false,
            "AttachStdout": false,
            "AttachStderr": false,
            "ExposedPorts": {
                "80/tcp": {}
            },
            "Tty": false,
            "OpenStdin": false,
            "StdinOnce": false,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "NGINX_VERSION=1.21.4",
                "NJS_VERSION=0.7.0",
                "PKG_RELEASE=1~bullseye"
            ],
            "Cmd": [
                "nginx",
                "-g",
                "daemon off;"
            ],
            "Image": "sha256:2fb4060b053a39040c51ff7eadd30325de2c76650fc50aa42839070e16e8bdcb",
            "Volumes": null,
            "WorkingDir": "",
            "Entrypoint": [
                "/docker-entrypoint.sh"
            ],
            "OnBuild": null,
            "Labels": {
                "maintainer": "NGINX Docker Maintainers <docker-maint@nginx.com>"
            },
            "StopSignal": "SIGQUIT"
        },
        "Architecture": "amd64",
        "Os": "linux",
        "Size": 141490847,
        "VirtualSize": 141490847,
        "GraphDriver": {
            "Data": {
                "LowerDir": "/var/lib/docker/overlay2/256bdf16c37330447bc109e42e948b6fad24a5fcb4a0c3ec3dd1f15275d598be/diff:/var/lib/docker/overlay2/26a03a178bdea1d0c46cc60ce8e747815f88aa66e7047a6fee94e6c37337b83d/diff:/var/lib/docker/overlay2/05b6dcc39d0c0c545d9c208e2115dc316a0d6cc36a9eb8751394576fa6c6bf75/diff:/var/lib/docker/overlay2/38848281d45670b1942db9590302bf448298004c3d8ed9fa026fbb265a1991ac/diff:/var/lib/docker/overlay2/2fc5a36e4d99dc45cbaa1277505ed9ff63e83863881759d14e8b712be61f1593/diff",
                "MergedDir": "/var/lib/docker/overlay2/1fb5e3906147a793d9c799c407e65a23f53c7f4dd86d828820bb1520e9686f86/merged",
                "UpperDir": "/var/lib/docker/overlay2/1fb5e3906147a793d9c799c407e65a23f53c7f4dd86d828820bb1520e9686f86/diff",
                "WorkDir": "/var/lib/docker/overlay2/1fb5e3906147a793d9c799c407e65a23f53c7f4dd86d828820bb1520e9686f86/work"
            },
            "Name": "overlay2"
        },
        "RootFS": {
            "Type": "layers",
            "Layers": [
                "sha256:e1bbcf243d0e7387fbfe5116a485426f90d3ddeb0b1738dca4e3502b6743b325",
                "sha256:37380c5830feb5d6829188be41a4ea0654eb5c4632f03ef093ecc182acf40e8a",
                "sha256:ff4c727794302b5a0ee4dadfaac8d1233950ce9a07d76eb3b498efa70b7517e4",
                "sha256:49eeddd2150fbd14433ec1f01dbf6b23ea6cf581a50635554826ad93ce040b68",
                "sha256:1e8ad06c81b6baf629988756d90fd27c14285da4d9bf57179570febddc492087",
                "sha256:8525cde30b227bb5b03deb41bda41deb85d740b834be61a69ead59d840f07c13"
            ]
        },
        "Metadata": {
            "LastTagTime": "0001-01-01T00:00:00Z"
        }
    }
]
