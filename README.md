This is a software that simulates some RF algorithms in Edge computing. I have added 5 algorithms to the software and they are: PPO, DQN, A2C, SAC and TRPO. Please feel free to contribute to this project.

Here are the guide to start the software:
1. Install Nodejs (I'm using node version 18.14.0):
    - wget [https://nodejs.org/dist/v18.14.0/node-v18.14.0.tar.gz](https://nodejs.org/dist/v18.14.0/node-v18.14.0-linux-x64.tar.gz)
    - tar -xf node-v18.14.0.tar.gz
    - export PATH={path to your node dir}/bin:$PATH
2. Create a Python virtual environment
    - You can use conda or what ever you have to create a Python virtual environment (python version should be 3.7.16)
3. Install server dependencies. You can follow these steps:
    - Activate your Python virtual environment
    - cd server/
    - pip install -r requirements.txt
4. Start server (your server will running in http://127.0.0.1:5000 by default) by using the command:
    - cd src/
    - flask --app app --debug run
5. Install UI packages
    - cd ui/
    - npm install
6. Start UI by using the command:
    - REACT_APP_API_ROOT=http://127.0.0.1:5000 npm start

*NOTE: When you run an algorithm, you may encounter an error due to missing a package called libopenmpi-dev. You can install this package by the command `sudo apt install libopenmpi-dev`.
