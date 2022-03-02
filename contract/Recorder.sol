pragma solidity ^0.5.0;
// 构建好的合约数据被保存在了build/contract目录下
contract Recorder {

    event RecordDone(address from, uint length);
    event prepareGiftDone(address from, uint length);
    // 从init task中继承过来
    uint taskReqNum = 2;

    uint writeCounter = 0;
    address[] partnerList;
    mapping(address => int[]) recorder;

    int[] gift;
    uint giftsLeft = 0;

    uint SNEpoch = 0;
    uint SNBatch = 0;

    // TODO: 需要防止重放攻击
    function writeCounterAdd() private returns (bool) {
        writeCounter += 1;
        return true;
    }

    function prepareGift() private returns (bool){
        uint len = recorder[partnerList[0]].length;
        giftsLeft = taskReqNum;
        for(uint i = 0; i < len; i++) {
            gift.push(recorder[partnerList[0]][i]);
        }
        for(uint i = 1; i < partnerList.length; i++) {
            for(uint k = 0; k < len; k++)
                gift[k] += recorder[partnerList[i]][k];
            // 需要清空上一次的迭代值
            delete recorder[partnerList[i]];
        }
        return true;
    }
    // TODO: function resetGift() private {gift = 0;} 需要么?

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
    function recordPara(int[] memory para, uint epoch, uint batch) public returns (bool) {
        // TODO: 防止一个节点在一次batch内上传多次
        // 检查是否需要更新Epoch Numb
        updateSNEpochBatch(epoch, batch);
        // 如果MLNode传来的Epoch小于当前记录的Epoch, 则返回false
        // TODO: (ML行为/待商讨) 若返回false时代表着该节点计算的太慢了
        if (epoch < SNEpoch) {return false;}
        if (batch < SNBatch) {return false;}
        // 记录本地计算出的参数
        for (uint i = 0; i < para.length; i++) {
            recorder[msg.sender].push(para[i]);
        }
        // 记录传递参数的MLNode信息
        partnerList.push(msg.sender);

        // 调用合并函数并清空当前的数组
        // emit RecordDone(msg.sender, para.length);
        if (partnerList.length >= taskReqNum) {
            if (prepareGift() == true) {
                delete partnerList;
                emit prepareGiftDone(msg.sender, gift.length);
            } else {
                // TODO: failed 事件
            }
        } else {
            // 返回记录成功的事件(log)
            emit RecordDone(msg.sender, para.length);
        }
        return true;
    }

    // 当MLNode监听到prepareGiftDone事件时可调用此方法
    // TODO: 原子性检查
    /*
    function getGift() public returns (uint, uint, int[] memory) {
        if (giftsLeft <= 0) {
            // 需要设置一个特殊的编码
            // TODO: (待商讨; MLNode行为)如果SNEpoch小于本地Epoch 则本地等待?
            return (giftsLeft, SNEpoch, gift);
        }
        giftsLeft -= 1;
        // 只有当gitsLeft不等与0时, MLNode才能认为其是正常的
        return (giftsLeft, SNEpoch, gift);
    } */
    function getGift() public view returns (uint, uint, int[] memory) {
        return (SNEpoch, SNBatch, gift);
    }

}