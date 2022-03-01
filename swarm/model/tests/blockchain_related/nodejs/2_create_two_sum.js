/* eslint-disable */
const { Conflux } = require('../../../../../sdk/js-conflux-sdk/'); // require('js-conflux-sdk');
let fs = require("fs")

const ROOT_DIR = "./contract/two_sum/"
let config = require(ROOT_DIR + "config.json");

const cfx = new Conflux({
  // 节点的地址和端口号，这里用的测试网。实际最好用最新的主网地址
  // url: config.rpc,
  url: 'http://localhost:12537/',
  defaultGasPrice: 100,
  defaultGas: 1000000,
  logger: console,
});

const accountAlice = cfx.Account('0xb205017cc1b95e12aa37784b3e66eaf099ba6cf0e80cf10f8fc87b44abba53a7');
const contract = cfx.Contract({
  abi: require(ROOT_DIR + 'abi.json'),
  bytecode: "0x" + require(ROOT_DIR + 'bytecode.json').bytecode
}).constructor();

function showContract() {
    console.log(contract);
}

/*
 deploy contract with parameters
 */
 async function deployContract() {
  try {
      let result = await contract.sendTransaction({from: accountAlice}).mined();
      console.log('result', JSON.stringify(result, null, 2));
      config.contract = result.contractCreated
      fs.writeFileSync(ROOT_DIR + "config.json", JSON.stringify(config, null, 4));
  } catch (e) {
      console.log(e);
  }
}


/*
 Warning! some example might send a transaction. please test them one by one
 */
// async function main() {
//     // showContract();
  
//     await deployContract();
//   }
  
//   main().finally(() => conflux.close());

let arguments = process.argv.splice(2);
if(arguments[0] === "deploy") {
  deployContract().then(_ => console.log("deploy contract complete"))
}

if(arguments[0] === "show") {
  showContract()
}