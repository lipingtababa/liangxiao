- E2E test should carry on from outside of the systems, simulating its clients with simulated requests. It shouldn't simulate its implmentation.

- Until there is an open pr in https://github.com/lipingtababa/liangxiao/pulls, sct is not working.

- Everytime you change the code, u run unit test to ensure nothing has been broken by your change. Also, you run integration test when you change the interfaces among modules.