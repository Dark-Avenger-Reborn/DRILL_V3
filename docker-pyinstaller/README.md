# PyInstaller Docker Images

**darkavengerreborn/pyinstaller-linux** and **darkavengerreborn/pyinstaller-windows**
are Docker/Podman containers designed to simplify the process of compiling Python applications into binaries/executables.

## Container registry

- [hub.docker.com](https://hub.docker.com/u/dark-darkavengerreborn)

  - `darkavengerreborn/pyinstaller-windows` / `docker.io/darkavengerreborn/pyinstaller-windows`
  - `darkavengerreborn/pyinstaller-linux` / `docker.io/darkavengerreborn/pyinstaller-linux`


## Usage

There are three containers, one for `Linux` and one for `Windows` builds.
The Windows builder runs `Wine` inside Ubuntu to emulate Windows in Docker.

To build your application, you need to mount your source code into the `/src/` volume.

The source code directory should have your `.spec` file that PyInstaller generates. If you don't have one, you'll need to run PyInstaller once locally to generate it.

If the `src` folder has a `requirements.txt` file, the packages will be installed into the environment before PyInstaller runs.

For example, in the folder that has your source code, `.spec` file and `requirements.txt`:

```sh
docker run \
  --volume "$(pwd):/src/" \
  darkavengerreborn/pyinstaller-windows:latest
```

will build your PyInstaller project into `dist/`. The `.exe` file will have the same name as your `.spec` file.

```sh
docker run \
  --volume "$(pwd):/src/" \
  darkavengerreborn/pyinstaller-linux:latest
```

will build your PyInstaller project into `dist/`. The binary will have the same name as your `.spec` file.

### How do I specify the spec file from which the executable should be build?

You'll need to pass an environment variable called `SPECFILE` with the path (relative or absoulte) to your spec file, like so:

```sh
docker run \
  --volume "$(pwd):/src/" \
  --env SPECFILE=./main-nogui.spec \
  darkavengerreborn/pyinstaller-linux:latest
```

This will build the executable from the spec file `main-nogui.spec`.

### How do I install system libraries or dependencies that my Python packages need?

You'll need to supply a custom command to Docker to install system pacakges. Something like:

```sh
docker run \
  --volume "$(pwd):/src/" \
  --entrypoint /bin/sh darkavengerreborn/pyinstaller-linux:latest \
  -c "apt update -y && apt install -y wget && /entrypoint.sh"
```

Replace `wget` with the dependencies / package(s) you need to install.

### How do I generate a .spec file?

```sh
docker run \
  --volume "$(pwd):/src/" \
  darkavengerreborn/pyinstaller-linux:latest \
  "pyinstaller --onefile your-script.py"
```

will generate a `spec` file for `your-script.py` in your current working directory. See the PyInstaller docs for more information.

### How do I change the PyInstaller version used?

Add `pyinstaller==6.9.0` to your `requirements.txt`.

### Is it possible to use a package mirror?

Yes, by supplying the `PYPI_URL` and `PYPI_INDEX_URL` environment variables that point to your PyPi mirror.

## Star History

<a href="https://star-history.com/#darkavengerreborn/docker-pyinstaller&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=darkavengerreborn/docker-pyinstaller&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=darkavengerreborn/docker-pyinstaller&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Dark-Avenger-Reborn/docker-pyinstaller&type=Date" />
 </picture>
</a>

## License

MIT
