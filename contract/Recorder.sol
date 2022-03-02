pragma solidity ^0.5.0;
// 构建好的合约数据被保存在了build/contract目录下
contract Recorder {

    event RecordDone(address from, int amount);
    event prepareGiftDone(address from, int amount);
    // 从init task中继承过来
    uint taskReqNum = 2;

    uint writeCounter = 0;
    address[] partnerList;
    mapping(address => int) recorder;

    int gift = 0;
    uint giftsLeft = 0;
    
    uint SNEpoch = 0;
    
    // TODO: 需要防止重放攻击
    function writeCounterAdd() private returns (bool) {
        writeCounter += 1;
        return true;
    }

    function prepareGift() private returns (bool){
        gift = 0;
        giftsLeft = taskReqNum;
        for(uint i = 0; i < partnerList.length; i++) {
            gift += recorder[partnerList[i]];
            // 需要清空上一次的迭代值
            recorder[partnerList[i]] = 0;
        }
        return true;
    }
    // TODO: function resetGift() private {gift = 0;} 需要么?

    function updateSNEpoch(uint epoch) private {
        if (partnerList.length == 0 && epoch > SNEpoch) {
            SNEpoch = epoch;
        }
    }

    // MLNode在callBack中调用的函数, 用于记录本地计算出来的参数以及参数所属的伦次
    function recordPara(int para, uint epoch) public returns (bool) {
        // 检查是否需要更新Epoch Numb
        updateSNEpoch(epoch);
        // 如果MLNode传来的Epoch小于当前记录的Epoch, 则返回false
        // TODO: (ML行为/待商讨) 若返回false时代表着该节点计算的太慢了
        if (epoch < SNEpoch) {return false;}
        // 记录本地计算出的参数
        recorder[msg.sender] = para;
        // 记录传递参数的MLNode信息
        partnerList.push(msg.sender);
        // 返回记录成功的事件(log)
        emit RecordDone(msg.sender, para);
        // 调用合并函数并清空当前的数组
        if (partnerList.length >= taskReqNum) {
            if (prepareGift() == true) {
                delete partnerList;
                emit prepareGiftDone(msg.sender, gift);
            } else {
                // TODO: failed 事件
            }
        }
        return true;
    }

    // 当MLNode监听到prepareGiftDone事件时可调用此方法
    // TODO: 原子性检查
    function getGift() public returns (uint, uint, int) {
        if (giftsLeft <= 0) {
            // 需要设置一个特殊的编码
            // TODO: (待商讨; MLNode行为)如果SNEpoch小于本地Epoch 则本地等待?
            return (giftsLeft, SNEpoch, 0);
        }
        giftsLeft -= 1;
        // 只有当gitsLeft不等与0时, MLNode才能认为其是正常的
        return (giftsLeft, SNEpoch, gift);
    }

}