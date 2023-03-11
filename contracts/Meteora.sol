// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;
pragma experimental ABIEncoderV2;
 

import "@openzeppelin/contracts/utils/Strings.sol";
import {ECC} from "./ECC.sol";



 
 contract Meteora{

    int constant ringMember = 2; //v+1 aus wallet

    struct TestStruct{
        uint256[] test;
    }


    struct TXoutput{
        uint256 rPubKey;
        uint256[2] amountCommitment;
        uint16 transactionIndex; //used as t in one-time key creation
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
    function receiveTransaction(uint256 _message, uint256 c1,
        uint256[2] memory keyImage, //2d point 
        uint256[ringMember*2] memory rFactors, //array of 2 commitments being 2d points
        uint256[2][2][ringMember] memory inputs,
        uint256 rPubKey,
        uint256[2] memory amountCommitment,
        uint16  transactionIndex) public returns (bool){

        

        MLSAG memory _signatures;
        

        _signatures.c1 = c1;
        _signatures.keyImage = keyImage;
        _signatures.rFactors = rFactors;
        _signatures.inputs = inputs;


        require(this.checkKeyImage(keyImage),
        "The provided keyImage has been used before!");
        //for (uint256 i = 0; i < _signatures.length; i++) {
                
                //check that all signatures are correct
                //hier wurde [i] entfernt
        require(this.verifyTransaction(_message, _signatures), 
        "The provided signatures were incorrect! \n The transaction will be canceled. ");

        
        //}

        //for (uint256 i = 0; i < _signatures.length; i++) {
            //hier wurde [i] entfernt
            usedKeyImages.push((_signatures.keyImage));
        //} 

        //for (uint256 i = 0; i < _outputs.length; i++) {
            //hier wurde [i] entfernt
            //TXoutputs.push((_outputs));
        //}

        
        //event fehlt []
        //emit TransactionApproved(_outputs);
        emit TestEvent(123);

        

        return true;
    }


    function verifyTransaction(uint256 _message, MLSAG memory _signature) public returns (bool){

            
            
            TmpStruct memory tmpStruct;

            uint256[ringMember+1] memory c;

            

            uint256[2] memory keyImage = _signature.keyImage;

            


            uint256[2][2][ringMember] memory ring = _signature.inputs;

            //return _signature.rFactors;

            
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

                //r1 = sig[i][0][j]
                //r2 = sig[i][0][j+1]

                /*if(j >= 4){
                return l;
                }*/

                K1 = ring[l][0];
                K2 = ring[l][1];

                //K1 = ring[l][0]
                //K2 = ring[l][1]

                

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

            //return [tmpStruct.tmp1,tmpStruct.tmp2,tmpStruct.tmp3,tmpStruct.tmp4,tmpStruct.tmp5,tmpStruct.tmp6];



            

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

    function returnStruct(TestStruct memory _struct) public pure   returns (TestStruct memory){
        return _struct;
    }

    function returnMLSAG(MLSAG memory _mlsag) public pure   returns (MLSAG memory){
        return _mlsag;
    }


    event TransactionApproved (TXoutput _outputs);
    event TestEvent(uint256 num);

    
    function point2String(uint256[2] memory _point) internal view returns (string memory){
        //has to be exactly like in wallet
        return string.concat(Strings.toString(_point[0]),Strings.toString(_point[1]));
    }
    
    function hash2Hex(string memory _message) internal view returns (uint256){
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
 