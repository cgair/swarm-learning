/* eslint-disable */
const { Conflux } = require('../../../../../sdk/js-conflux-sdk/'); // require('js-conflux-sdk');
let fs = require("fs")
let config = require("./contract/two_sum/config.json");

const cfx = new Conflux({
  // 节点的地址和端口号，这里用的测试网。实际最好用最新的主网地址
  // url: config.rpc,
  url: 'http://localhost:12537/',
  defaultGasPrice: 100,
  defaultGas: 1000000,
  logger: console,
});

const accountAlice = cfx.Account('0xb205017cc1b95e12aa37784b3e66eaf099ba6cf0e80cf10f8fc87b44abba53a7');

function showContract() {
    console.log(contract);
}

async function set(value) {
    config = require("./contract/two_sum/config.json");
    const contract = cfx.Contract({
        abi: require('./contract/two_sum/abi.json'),
        address: config.contract
    });
    return await contract.add(value).sendTransaction({from: accountAlice}).mined();
}

let arguments = process.argv.splice(2);
if(arguments[0] === "set") {
    set(arguments[1], arguments[2]).then(_ => console.log("set complete"))
}

if(arguments[0] === "show") {
  showContract()
}