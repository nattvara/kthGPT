# kthGPT <!-- omit in toc -->

kthGPT is a free and open source tool that can watch a lecture for you. It allows students to ask questions about any lecture using the GPT-3 model.

> This project **is not** affiliated with KTH. It's just a tool that's meant to be useful for KTH students.

![Hero image](docs/img/hero.png)

# Table of Contents <!-- omit in toc -->

- [Usage](#usage)
  - [1. Select lecture](#1-select-lecture)
  - [2. Wait for kthGPT to "watch" the lecture](#2-wait-for-kthgpt-to-watch-the-lecture)
  - [3. Ask questions about the lecture](#3-ask-questions-about-the-lecture)
- [Run the tool locally](#run-the-tool-locally)
  - [Docker](#docker)
  - [Development](#development)
- [Testsuite](#testsuite)
- [Screenshots](#screenshots)
- [License](#license)

## Usage

kthGPT is available at [https://kthgpt.com](https://kthgpt.com) - it's free to use!

### 1. Select lecture

Select a lecture that's already been watched or add a new one! kthGPT can watch lectures hosted on [KTH Play](https://play.kth.se/) or [YouTube](https://youtube.com).

It can't watch any video on YouTube. Due to limited capacity kthGPT will only watch "relevant videos". Relevant videos are such that it thinks are `Recorded Lectures`. kthGPT uses a sample of the video to do this assessment.

### 2. Wait for kthGPT to "watch" the lecture

If the video has not been watched by kthGPT before, it will start watching the video and try to produce a summary. It will only listen to the audio, so nothing been shown or written in the lecture will be included in the summary.

This process is very resource intensive and usually takes between 20-60 minutes. This will be slower if many videos have been queued.

If the audio quality in the video is bad, the quality of the summary will be worse. kthGPT is generally best at understanding English. However, if the audio quality is good, Swedish should be just fine as well.

### 3. Ask questions about the lecture

The lecture is ready. kthGPT can now use GPT-3 to answer questions about the lecture. Some useful queries:

**- Summarize the lecture for me into 10 bullets**
>
> This query obviously useful to get a brief overview about what's covered in the lecture

**- Tell me the core concepts covered in the lecture and give some explanations for each**
>
> This usually produce very good results. Answers seem to be less inclined to summarise the audio transcript and focus more on the topics. Which seem to produce more accurate results.

**- At which point in the lecture is X covered?**
>
> Pretty self explanatory, useful to quickly now where to look in a lecture.

**- Where in the course book "X" can i read more about the topics from this lecture?**
>
> Very useful to find more reading instructions.
>
> In [this lecture](https://kthgpt.com/questions/lectures/0_xkulq3st/en) the following question:
>
> - _Where in the course book "Hans Peters, Game Theory: A Multi-Leveled Approach, Springer 2008" can i read more about the topics from this lecture?_
>
> Produce the following results
> - Hans Peters, Game Theory: A Multi-Leveled Approach, Springer 2008 (Chapter 6) provides a deep exploration of the topics discussed in this lecture. It includes discussion on transferable utility and the core, super-aditivity, and finding efficient outcomes in non-zero sum games, as well as balancing games and linear programming.
>

**- If i didn't attend this lecture what would I have to read-up on?**
>
> Tends to produce quite brief answers, with very "google:able" keywords.

## Run the tool locally

### Docker

The easiest way to run kthGPT locally is using [docker](https://www.docker.com/).

Update the environment.

```bash
cp .env.example .env
```

Make sure to update `OPENAI_API_KEY=sk-xxx...` with an API key from OpenAI [available here](https://platform.openai.com/account/api-keys).


```bash
# If host machine is running ARM (eg. M1 macs)
export DOCKER_DEFAULT_PLATFORM=linux/amd64

# Start the application
docker-compose up

# Download the course list
docker exec -it api sh -c "fetch_kth_courses"
```

The application should now be available on [http://localhost:1337](http://localhost:1337).

### Development

The following commands are useful to get the project setup for local development.

Clone the repo

```bash
git clone https://github.com/nattvara/kthGPT.git
cd kthGPT
```

```bash
python --version
# Python 3.10.8   Tested with this version
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
python setup.py develop
playwright install
playwright install-deps
```

Start the database.

```bash
docker run --name db -p 5432:5432 -e POSTGRES_PASSWORD=postgres -d postgres

psql -h 127.0.0.1 -p 5432 -U postgres -c "CREATE DATABASE kthgpt;" # password: postgres

# Create the database
create_db_schema
```

Start the redis server (used as backend for the job server).

```bash
docker run --name redis -d -p 6379:6379 redis redis-server --requirepass redis
```

Start the OpenSearch index.

```bash
docker run -p 9200:9200 -p 9600:9600 -e "discovery.type=single-node" --name opensearch -d opensearchproject/opensearch:latest
```

Start a queue worker.

```bash
rq worker --with-scheduler --url='redis://:redis@localhost:6379' default download extract transcribe summarise monitoring approval metadata
rq worker --with-scheduler --url='redis://:redis@localhost:6379' gpt # gpt queue must run on at least one separate worker
```

Start the web server.

```bash
uvicorn api:main --reload
```

Start the frontend.

```bash
# make sure pnpm is installed
npm install -g pnpm

cd web-ui
pnpm install

npm run dev
```

## Testsuite

To run the testsuite execute the following command in the repository root.

```bash
$ pytest
===================== test session starts ======================
collected 5 items

tests/feature/api/test_index.py .                        [ 20%]
tests/feature/api/test_lectures.py .                     [ 40%]
tests/feature/jobs/test_download_lecture.py .            [ 60%]
tests/unit/tools/video/test_img.py ..                    [100%]

====================== 5 passed in 0.78s =======================
```

## Screenshots

> ### Select a KTH Play or YouTube lecture

![Select](docs/img/select.png)

> ### Wait for kthGPT to watch the lecture

![Analyse](docs/img/analyse.png)

> ### Ask questions about the lecture

![Questions](docs/img/question.png)

## License

MIT ?? Ludwig Kristoffersson

See [LICENSE file](LICENSE) for more information.
