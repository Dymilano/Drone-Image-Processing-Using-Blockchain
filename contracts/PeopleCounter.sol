// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PeopleCounter {
    struct Analysis {
        uint timestamp;
        uint peopleCount;
        uint[8] percentLevels; // phần trăm cho các mức 10,20,30,40,50,70,90,100
        string sourceType; // camera, video, image
        string fileHash; // hash file ảnh/video nếu có
    }
    Analysis[] public analyses;
    event Analyzed(uint indexed id, uint timestamp, uint peopleCount, uint[8] percentLevels, string sourceType, string fileHash);

    function addAnalysis(uint _peopleCount, uint[8 ] memory _percentLevels, string memory _sourceType, string memory _fileHash) public {
        Analysis memory a = Analysis(block.timestamp, _peopleCount, _percentLevels, _sourceType, _fileHash);
        analyses.push(a);
        emit Analyzed(analyses.length-1, block.timestamp, _peopleCount, _percentLevels, _sourceType, _fileHash);
    }

    function getAnalysis(uint idx) public view returns (Analysis memory) {
        return analyses[idx];
    }

    function getCount() public view returns (uint) {
        return analyses.length;
    }
} 