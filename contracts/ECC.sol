// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "./EllipticCurve.sol";


contract ECC{

    uint256 public constant GeneratorX = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798;
    uint256 public constant GeneratorY = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8;

    uint256 public constant AA = 0;
    uint256 public constant BB = 7;

    uint256 public constant PP = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f;

    uint256 public constant GX = 0x6fb13b7e8ab1c7d191d16197c1bf7f8dc7992412e1266155b3fb3ac8b30f3ed8;
    uint256 public constant GY = 0x2e1eb77bd89505113819600b395e0475d102c4788a3280a583d9d82625ed8533;

    uint256 public constant HX = 0x07cd9ee748a0b26773d9d29361f75594964106d13e1cad67cfe2df503ee3e90e;
    uint256 public constant HY = 0xd209f7c16cdb6d3559bea88c7d920f8ff077406c615da8adfecdeef604cb40a6;

    uint256 public constant L = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141;


    function addPoints(uint256[2] memory _a, uint256[2] memory _b) external pure returns(uint256[2] memory) {

        (uint256 x, uint256 y)  = EllipticCurve.ecAdd(_a[0], _a[1], _b[0], _b[1], AA, PP);
        return [x,y];

    }

    function subPoints(uint256[2] memory _a, uint256[2] memory _b) external pure returns(uint256[2] memory) {
        (uint256 x, uint256 y)  = EllipticCurve.ecSub(_a[0], _a[1], _b[0], _b[1], AA, PP);
        return [x,y];

    }

    function mulPoint(uint256[2] memory _a, uint256 _scalar) external pure returns (uint256[2] memory){
        (uint256 x, uint256 y)  = EllipticCurve.ecMul(_scalar, _a[0], _a[1], AA, PP);
        return [x,y];

    }

    function mulG(uint256 _scalar) external pure returns (uint256[2] memory){
        (uint256 x, uint256 y)  = EllipticCurve.ecMul(_scalar, GX, GY, AA, PP);
        return [x,y];

    }

        function mulH(uint256 _scalar) external pure returns (uint256[2] memory){
        (uint256 x, uint256 y)  = EllipticCurve.ecMul(_scalar, HX, HY, AA, PP);
        return [x,y];

    }

    
   

    



}