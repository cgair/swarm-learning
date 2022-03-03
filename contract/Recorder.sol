pragma solidity ^0.5.0;

// TEST data

contract Recorder {
    uint constant sliceSize = 16384;
    event RecordDone(address from, uint length);
    event prepareGiftDone(address from, uint length);

    // 从init task中继承过来
    uint taskReqNum = 2;

    // 用于存储参数 TODO: NestedMapping
    address[] partnerList;
    mapping(address => int128[sliceSize]) recorder;

    // 控制字段
    uint SNEpoch = 0;
    uint SNBatch = 0;
    mapping(address => mapping(uint => mapping(uint =>bool))) uploaded;

    // 账户地址 -> 控制字段 -> 字段对应的参数
    //mapping(address => mapping(uint => mapping(uint =>uint[256]))) paramaters;

    int128[sliceSize] gift;

    struct taskCtrl {
        uint id;
        address[] partnerList;
        mapping(address => bool) uploaded;
    }

    function prepareGift() private returns (bool){
        // 每次准备之前先进行初始化
        delete gift;
        /*
        for(uint i = 0; i < sliceSize; i++) {
            gift[i] = 0;
        } */
        for(uint i = 0; i < partnerList.length; i++) {
            for(uint k = 0; k < sliceSize; k++)
                gift[k] += recorder[partnerList[i]][k];
            // 每一个客户端传来的参数被加后需要被清空
            delete recorder[partnerList[i]];
        }
        return true;
    }

    function updateSNEpochBatch(uint epoch, uint batch) private {
        // 更新Epoch
        if (partnerList.length == 0 && epoch > SNEpoch) {
            SNEpoch = epoch;
            SNBatch = batch;
        }
        // 在同一个Epoch内更新Batch
        if (partnerList.length == 0 && epoch == SNEpoch && batch > SNBatch) {
            SNBatch = batch;
        }
    }

    // MLNode在callBack中调用的函数, 用于记录本地计算出来的参数以及参数所属的伦次
    function recordPara(uint128 epoch, uint128 batch, int128[sliceSize] memory para) public returns (bool) {
        // "Node already uploaded!"
        assert(uploaded[msg.sender][SNEpoch][SNBatch]  == false);
        // 检查是否需要更新Epoch Numb
        updateSNEpochBatch(epoch, batch);
        // 如果MLNode传来的Epoch小于当前记录的Epoch, 则返回终止
        // TODO: (ML行为/待商讨) 若返回false时代表着该节点计算的太慢了
        // "Uploading paramaters are not belong to Global Epoch/Batch");
        assert(epoch == SNEpoch);
        assert(batch == SNBatch);
        uploaded[msg.sender][SNEpoch][SNBatch] = true;

        // 记录本地计算出的参数
        for (uint i = 0; i < sliceSize; i++) {
            recorder[msg.sender][i] = para[i];
        }
        // 记录传递参数的MLNode信息
        partnerList.push(msg.sender);

        // TOFIX: 调用合并函数并清空当前的数组
        // emit RecordDone(msg.sender, para.length);
        if (partnerList.length >= taskReqNum) {
            if (prepareGift() == true) {
                delete partnerList;
                emit prepareGiftDone(msg.sender, gift.length);
            }
        } else {
            emit RecordDone(msg.sender, para.length);
        }
        return (true);
    }

    // 当MLNode监听到prepareGiftDone事件时可调用此方法
    function getGift() public view returns (uint, uint, int128[sliceSize] memory) {
        return (SNEpoch, SNBatch, gift);
    }

}