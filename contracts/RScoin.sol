// SPDX-License-Identifier: MIT
pragma solidity <0.7.0;
 
import "./math/SafeMath.sol"; 
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "./EllipticCurve.sol";
 
 contract RScoin is ERC20 {

    struct OpenOutput{
        uint256 pubKey;
        uint256 amountCommitment;
        uint16 transactionIndex; //used as t in one-time key creation
    }

    struct MLSAG{

        uint256 c1;
        uint256[2] keyImage; //2d point 
        uint256[] rFactors; //array of 2 commitments being 2d points

    }

    struct Message{

        uint256[][2] keyImages; // list of 2d points


    }





    address payable owner;

    mapping(uint256 => OpenOutput) openOutput2data;


    uint256[] openOutputs;
    uint256[] usedKeyImages;

    uint256 private _totalSupply;
    string private _name = "RScoin";
    string private _symbol = "RSC";

    
    constructor(uint totalSupply_ ) ERC20("RScoin","RSC"){
        _totalSupply = totalSupply_;
        owner = payable(msg.sender);

        _mint(owner, _totalSupply/10);
    }

    function verifyTransaction(string message, uint256[] signature) returns (bool){

        for (uint256 i = 0; i < signature.length; i++) {

            uint256 keyImage = signature[i][1];
            uint256[] ring = signature[i][2];
            
            
            mapping (uint256 => uint256) c;
            c[0] = int(sig[i][0][0],16)
            l = 0
            r = []
            k = []

            
        }


        return true
    }


   //function transfer(to, amount) public virtual override returns (bool){
   // return True;
   //};
    
 }
 