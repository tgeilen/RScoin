// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;
pragma experimental ABIEncoderV2;
 

import "@openzeppelin/contracts/utils/Strings.sol";
import {ECC} from "./ECC.sol";



 
 contract Meteora{

    int constant ringMember = 2; //v+1 aus wallet

    struct TXoutput{
        uint256 rPubKey;
        uint256[2] amountCommitment;
        uint16 transactionIndex; //used as t in one-time key creation
        uint256[2] txOAddress;
    }

    struct MLSAG{

        uint256 c1;
        uint256[2] keyImage; //2d point 
        uint256[ringMember * 2] rFactors; //array of 2 commitments being 2d points
        uint256[2][2][ringMember] inputs; //list of addresses used in signature (real and fake)

    }

    struct TmpStruct {
        uint256[2]  tmp1;
        uint256[2]  tmp2;
        uint256[2]  tmp3;
        uint256[2]  tmp4;
        uint256[2]  tmp5;
        uint256[2]  tmp6;
    }

    address payable owner;

    mapping(uint256 => TXoutput) openOutput2data;


    TXoutput[] private TXoutputs;
    uint256[2][] private usedKeyImages;

    string private _name = "Meteora";
    string private _symbol = "MET";

    ECC ecc = new ECC();

    
    constructor() {
        owner = payable(msg.sender);

        
    }

    //hier wurde [i] entfernt bei MLSAG und TXoutput
    //function receiveTransaction(uint256 _message, MLSAG memory _signatures, TXoutput memory _outputs) public returns (bool){
    function receiveTransaction(uint256 _message, uint256 _c1,
        uint256[2] memory _keyImage, //2d point 
        uint256[ringMember*2] memory _rFactors, //array of 2 commitments being 2d points
        uint256[2][2][ringMember] memory _inputs,
        uint256 _rPubKey,
        uint256[2] memory _amountCommitment,
        uint16  _transactionIndex,
        uint256[2] memory _txOAddress) public returns (bool){

        

        MLSAG memory signature;
        

        signature.c1 = _c1;
        signature.keyImage = _keyImage;
        signature.rFactors = _rFactors;
        signature.inputs = _inputs;


        require(this.checkKeyImage(_keyImage),
        "The provided keyImage has been used before!");
        //for (uint256 i = 0; i < _signatures.length; i++) {
                
                //check that all signatures are correct
                //hier wurde [i] entfernt
        require(this.verifyTransaction(_message, signature), 
        "The provided signatures were incorrect! \n The transaction will be canceled. ");

        
        //}

        //for (uint256 i = 0; i < _signatures.length; i++) {
            //hier wurde [i] entfernt
            usedKeyImages.push((signature.keyImage));
        //} 

        //for (uint256 i = 0; i < _outputs.length; i++) {
            //hier wurde [i] entfernt
            //TXoutputs.push((_outputs));
        //}

        
        //event fehlt []
        //emit TransactionApproved(_outputs);
        

        this.receiveOutput(_rPubKey, _amountCommitment, _transactionIndex, _txOAddress);

        

        return true;
    }


    function verifyTransaction(uint256 _message, MLSAG memory _signature) public view returns (bool){

            
            
            TmpStruct memory tmpStruct;

            uint256[ringMember+1] memory c;

            uint256[2] memory keyImage = _signature.keyImage;
            uint256[2][2][ringMember] memory ring = _signature.inputs;
            c[0] = _signature.c1;

            uint256 l = 0;

            uint256 r1;
            uint256 r2;

            uint256[2] memory K1;
            uint256[2] memory K2;

            string memory message;

            uint256 j;

            
           
            for (j = 0; j < _signature.rFactors.length-2; j=j+2) {
            //for (j = 0; j < 6; j=j+2) {

                message = "";
                r1 = _signature.rFactors[j];
                r2 = _signature.rFactors[j+1];

                K1 = ring[l][0];
                K2 = ring[l][1];
                

                //need to avoid stack too deep error
                tmpStruct.tmp1 = ecc.mulG(r1);
                tmpStruct.tmp2 = ecc.mulPoint(K1,c[l]);
                tmpStruct.tmp3 = ecc.mulPoint(hash2Point(K1),r1);
                tmpStruct.tmp4 = ecc.mulPoint(keyImage,c[l]);
                tmpStruct.tmp5 = ecc.mulG(r2);
                tmpStruct.tmp6 = ecc.mulPoint(K2,c[l]);

                            
                
                message = string.concat(
                                Strings.toString(_message), 
                                point2String(ecc.addPoints(tmpStruct.tmp1,tmpStruct.tmp2)));

                message = string.concat(message,
                                point2String(ecc.addPoints(tmpStruct.tmp3,tmpStruct.tmp4)));

                message = string.concat(message,
                                point2String(ecc.addPoints(tmpStruct.tmp5,tmpStruct.tmp6)));

                
                //return message;
                c[l+1] = hash2Hex(message);

                l++; 
                                       
            }


            
           message = "";

            j = _signature.rFactors.length-2;

            r1 = _signature.rFactors[j];
            r2 = _signature.rFactors[j+1];

            

            K1 = ring[l][0];
            K2 = ring[l][1];

            

            

            //need to avoid stack too deep error
            tmpStruct.tmp1 = ecc.mulG(r1);
            tmpStruct.tmp2 = ecc.mulPoint(K1,c[l]);
            tmpStruct.tmp3 = ecc.mulPoint(hash2Point(K1),r1);
            tmpStruct.tmp4 = ecc.mulPoint(keyImage,c[l]);
            tmpStruct.tmp5 = ecc.mulG(r2);
            tmpStruct.tmp6 = ecc.mulPoint(K2,c[l]);


               message = string.concat(
                                Strings.toString(_message), 
                                point2String(ecc.addPoints(tmpStruct.tmp1,tmpStruct.tmp2)));

                message = string.concat(message,
                                point2String(ecc.addPoints(tmpStruct.tmp3,tmpStruct.tmp4)));

                message = string.concat(message,
                                point2String(ecc.addPoints(tmpStruct.tmp5,tmpStruct.tmp6)));
                                                                
                   
            uint256 calcC = hash2Hex(message);

            
            return c[0] == calcC;


            
           
            
            
       
    }


    function checkKeyImage(uint256[2] memory keyImage) public view returns (bool){
        uint256[2] memory usedKeyImage;
        for (uint256 index = 0; index < usedKeyImages.length; index++) {
            usedKeyImage = usedKeyImages[0];
            if(keyImage[0] == usedKeyImage[0] && keyImage[1] == usedKeyImage[1]){
                return false;
            }
        }
        return true;
    }

    function receiveOutput(uint256 _rPubKey,
        uint256[2] memory _amountCommitment,
        uint16  _transactionIndex,
        uint256[2] memory _txOAddress) public returns (bool){
            //this function is used to fill contract with inital outputs after creation
            
        TXoutput memory txOutput;

        txOutput.rPubKey = _rPubKey;
        txOutput.amountCommitment = _amountCommitment;
        txOutput.transactionIndex = _transactionIndex;
        txOutput.txOAddress = _txOAddress;

        TXoutputs.push(txOutput);

        return true;
            
    }


    function getTXoutputs() public view  returns (TXoutput[] memory){

        return TXoutputs;
    }

        function returnKeyImage() public view returns (uint256[2][] memory){
        return usedKeyImages;
    }





     function getInfo() public pure   returns (string memory){
        return "Hello World";
     }

    function returnNum(uint256 _num) public pure   returns (uint256){
        return _num;
    
    }



    function returnArr(uint256[] memory _arr) public pure   returns (uint256[] memory){
        return _arr;
    }


    function returnMLSAG(MLSAG memory _mlsag) public pure   returns (MLSAG memory){
        return _mlsag;
    }


    event TransactionApproved (TXoutput _outputs);
    

    
    function point2String(uint256[2] memory _point) internal pure returns (string memory){
        //has to be exactly like in wallet
        return string.concat(Strings.toString(_point[0]),Strings.toString(_point[1]));
    }
    
    function hash2Hex(string memory _message) internal pure returns (uint256){
        return uint256(keccak256(abi.encodePacked(_message)));
    }

    function hash2Point(string memory _message) internal view returns (uint256[2] memory){
        uint256 scalar = uint256(keccak256(abi.encodePacked(_message)));
        return ecc.mulG(scalar);
    }

    function hash2Point(uint256[2] memory _point) internal view returns (uint256[2] memory){
        string memory _message = point2String(_point);
        return hash2Point(_message);
    }





    



   
    
 }
 