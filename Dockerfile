FROM node:18.10.0
// 나에게 맞는 node 버전을 적어준다.

RUN mkdir -p /app
WORKDIR /app
ADD . /app
// mkdir 로 /app 폴더를 만들어서
// 경로를 /app 으로 이동한 뒤에
// ADD 로 모든 파일을 /app 으로 복사한다

RUN npm install
// yarn 이면 yarn install 하면 되겠지? yarn build 인가?
// 이 명령어가 틀리면 Actions 가 돌아가다 에러가 발생하니 에러가 나면 에러부분을 확인해보면서 고쳐주면 된다.

ENV HOST 0.0.0.0
EXPOSE 3000
// 모든 ip 에서 접근 가능
// 3000 포트 개방 포트 여러개를 개방하려면, EXPOSE 3000 80 이렇게 띄워서 써주면 된다.


CMD ["npm", "start"]
// CMD 는 여러개 적을 수도 있지만 마지막에 작성된 CMD 만 작동한다.
// 컨테이너에서 작동될 명령을 입력한다. yarn 이면 yarn start 를 적어주면 됨
