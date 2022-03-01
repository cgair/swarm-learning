const PRIVATE_KEY = '0x46b9e861b63d3509c88b7817275a30d22d62c8cd8fa6486ddee35ef0d8e0495f';
const { Conflux } = require('./js-conflux-sdk');

let fs = require("fs")

let config = require("./config.json");
const cfx = new Conflux({
    // 节点的地址和端口号，这里用的测试网。实际最好用最新的主网地址
    // url: config.rpc,
    url: 'http://localhost:12537/',
    defaultGasPrice: 100,
    defaultGas: 1000000,
    logger: console,
});

async function deploy() {
    const account = cfx.Account(PRIVATE_KEY);
    const contract = cfx.Contract({
        abi: require('./abi.json'),
        bytecode: "0x" + require('./bytecode.json').bytecode
    }).constructor();
    try {
        let result = await contract.sendTransaction({from: account}).mined();
        config.contract = result.contractCreated
        fs.writeFileSync("config.json", JSON.stringify(config, null, 4));
    } catch (e) {
        console.log(e);
    }

}

async function set(key, value) {
    config = require("./config.json");
    const account = cfx.Account(PRIVATE_KEY);
    const contract = cfx.Contract({
        abi: require('./abi.json'),
        address: config.contract
    });
    return await contract.setValue(key, value).sendTransaction({from: account}).mined();
}

async function get(key) {
    config = require("./config.json");
    const contract = cfx.Contract({
        abi: require('./abi.json'),
        address: config.contract
    });
    return await contract.configMapping(key);
}

async function getBlockByEpoch(epoch) {
    let result = await cfx.getBlockByEpochNumber(epoch, true);
    console.log(JSON.stringify(result));
}

let arguments = process.argv.splice(2);
if(arguments[0] === "deploy") {
    deploy().then(_ => console.log("deploy complete"))
} else if(arguments[0] === "set") {
    set(arguments[1], arguments[2]).then(_ => console.log("set complete"))
} else if(arguments[0] === "get") {
    get(arguments[1]).then(result => console.log(`get ${arguments[1]} result ${result}`));
}
