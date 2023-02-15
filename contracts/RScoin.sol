// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;
 
import "./math/SafeMath.sol"; 
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
 
 contract RScoin is ERC20 {

    address payable owner;

    uint256 private _totalSupply;
    string private _name = "RScoin";
    string private _symbol = "RSC";

    
    constructor(uint totalSupply_ ) ERC20("RScoin","RSC"){
        _totalSupply = totalSupply_;
        owner = payable(msg.sender);

        _mint(owner, _totalSupply/10);
    }


   //function transfer(to, amount) public virtual override returns (bool){
   // return True;
   //};
    
 }
 