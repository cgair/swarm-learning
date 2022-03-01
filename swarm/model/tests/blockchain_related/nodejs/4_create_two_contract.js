/* eslint-disable */
const { Conflux } = require('../../../../../sdk/js-conflux-sdk/'); // require('js-conflux-sdk');
let fs = require("fs")

const ROOT_DIR = "./contract/tests/"

const cfx = new Conflux({
  url: 'http://localhost:12537/',
  defaultGasPrice: 100,
  defaultGas: 1000000,
  logger: console,
});

const accountAlice = cfx.Account('0xb205017cc1b95e12aa37784b3e66eaf099ba6cf0e80cf10f8fc87b44abba53a7');


function showContract(contract1, contract2) {
    console.log(contract1);
    console.log(contract2);
}

/*
 deploy contract with parameters
 */
 async function deployContract(contract, config, write_path) {
  try {
      let result = await contract.sendTransaction({from: accountAlice}).mined();
      console.log('result', JSON.stringify(result, null, 2));
      config.contract = result.contractCreated
      fs.writeFileSync(write_path, JSON.stringify(config, null, 4));
  } catch (e) {
      console.log(e);
  }
}


const contract1 = cfx.Contract({
    abi: require(ROOT_DIR + 'recorder/abi.json'),
    bytecode: "0x" + require(ROOT_DIR + 'recorder/bytecode.json').bytecode
}).constructor();

const contract2 = cfx.Contract({
    abi: require(ROOT_DIR + 'task_handler/abi.json'),
    bytecode: "0x" + require(ROOT_DIR + 'task_handler/bytecode.json').bytecode
}).constructor();

let arguments = process.argv.splice(2);
if(arguments[0] === "deploy") {
    if(arguments[1] == "recoder") {
        let config = require(ROOT_DIR + "recorder/config.json");
        let write_path = ROOT_DIR + "recorder/config.json"
        deployContract(contract1, config, write_path).then(_ => console.log("deploy recoder contract complete"))
    }else if(arguments[1] === "handler") {
        let config = require(ROOT_DIR + "task_handler/config.json");
        let write_path = ROOT_DIR + "task_handler/config.json"
        deployContract(contract2, config, write_path).then(_ => console.log("deploy handler contract complete"))
    }else {
        console.log("Illege arguments");
    }
}else if(arguments[0] === "show") {
    showContract(contract1, contract2)
}