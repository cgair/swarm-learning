/**
 * "SPDX-License-Identifier:UNLICENSED" for non-open-source code. Please see https://spdx.org from more information.
 */

 pragma solidity ^0.8.0;

 contract LightSealerNFT {
 
     // The total of the NFT
     uint256 private _totalSupply ;
 
     // Mapping from token ID to owner address
     mapping(uint256 => address) private _owners;
 
     // Mapping owner address to token count
     mapping(address => uint256) private _balances;
 
     // Mapping from token ID to approved address
     mapping(uint256 => address) private _tokenApprovals;
 
     // Mapping from owner to operator approvals
     mapping(address => mapping(address => bool)) private _operatorApprovals;
 
     // Light Sealer NFT Entity
     struct NFTProduction {
         uint256 tokenID;
         string  productionID;
     }
 
     // Light Sealer NFT production information
     mapping(uint256 => NFTProduction) private _nftProduction;
 
     event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
 
     event Approval(address indexed owner, address indexed to, uint256 indexed tokenId);
 
     event ApprovalForAll(address indexed owner, address indexed operator, bool indexed approved);
 
     event CreateNFT(address indexed owner, uint256 indexed startID, uint256 indexed endID);
 
     constructor() {
         _totalSupply = 0;
     }
 
 
     /**
      *  Init create NFT.
      */ 
      function createNFT(string[] memory _productionID) public {
         require(msg.sender != address(0), "Create NFT address not for zero address");
 
         uint256 _start = _totalSupply;
 
          for (uint16 i = 0; i < _productionID.length; i++ ) {
             _owners[_totalSupply] = msg.sender;
             NFTProduction memory _tmp = NFTProduction({tokenID: _totalSupply, productionID:_productionID[i]});
 
             _nftProduction[_totalSupply] = _tmp;
             _totalSupply += 1;
             _balances[msg.sender] += 1;
          }
 
          emit CreateNFT(msg.sender,_start, _totalSupply);
      }
 
     /**
      * Get Create NFT TokenID 
      */  
      function getCreateNFT(uint256 startId, uint256 endId) public view returns (NFTProduction[] memory) {
          require(startId <= endId, "NFT tokenID should continuous increase");
 
          NFTProduction[] memory _nft = new NFTProduction[](endId - startId);
 
          for (uint256 i = startId; i < endId; i++ ) {
             require(_exists(i), "ERC721: token not exist");
             _nft[i-startId] = _nftProduction[i];
          }
 
          return _nft;
      }
 
     function totalSupply() public view returns (uint256) {
         return _totalSupply;
     }
 
     /**
      *  query the production by tokenID.
      */ 
     function productionInfo(uint256 _tokenID) public view returns (NFTProduction memory) {
         require(_exists(_tokenID), "ERC721: token not exist");
 
         return _nftProduction[_tokenID];
     } 
 
     /**
      * query the NFT count by user address.
      */
     function balanceOf(address owner) public view returns (uint256) {
         require(owner != address(0), "ERC721: balance query for the zero address");
         return _balances[owner];
     }
 
     /**
      * query the tokenID belong to user.
      */
     function ownerOf(uint256 tokenId) public view returns (address) {
         address owner = _owners[tokenId];
         require(owner != address(0), "ERC721: owner query for nonexistent token");
         return owner;
     }
 
     function approve(address to, uint256 tokenId) public {
         address owner = LightSealerNFT.ownerOf(tokenId);
         require(to != owner, "ERC721: approval to current owner");
 
         require(
             _msgSender() == owner || isApprovedForAll(owner, _msgSender()),
             "ERC721: approve caller is not owner nor approved for all"
         );
 
         _approve(to, tokenId);
     }
 
     function _msgSender() public view returns (address) {
         return msg.sender;
     }
 
     function getApproved(uint256 tokenId) public view returns (address) {
         require(_exists(tokenId), "ERC721: approved query for nonexistent token");
 
         return _tokenApprovals[tokenId];
     }
 
     function setApprovalForAll(address operator, bool approved) public {
         require(operator != _msgSender(), "ERC721: approve to caller");
 
         _operatorApprovals[_msgSender()][operator] = approved;
         emit ApprovalForAll(_msgSender(), operator, approved);
     }
 
     function isApprovedForAll(address owner, address operator) public view returns (bool) {
         return _operatorApprovals[owner][operator];
     }
 
     function transferFrom(
         address from,
         address to,
         uint256 tokenId
     ) public {
         //solhint-disable-next-line max-line-length
         require(_isApprovedOrOwner(_msgSender(), tokenId), "ERC721: transfer caller is not owner nor approved");
 
         _transfer(from, to, tokenId);
     }
 
     function _exists(uint256 tokenId) internal view virtual returns (bool) {
         return _owners[tokenId] != address(0);
     }
 
     function _isApprovedOrOwner(address spender, uint256 tokenId) internal view virtual returns (bool) {
         require(_exists(tokenId), "ERC721: operator query for nonexistent token");
         address owner = LightSealerNFT.ownerOf(tokenId);
         return (spender == owner || getApproved(tokenId) == spender || isApprovedForAll(owner, spender));
     }
 
     function _transfer(
         address from,
         address to,
         uint256 tokenId
     ) internal {
         require(LightSealerNFT.ownerOf(tokenId) == from, "ERC721: transfer of token that is not own");
         require(to != address(0), "ERC721: transfer to the zero address");
 
         // Clear approvals from the previous owner
         _approve(address(0), tokenId);
 
         _balances[from] -= 1;
         _balances[to] += 1;
         _owners[tokenId] = to;
 
         emit Transfer(from, to, tokenId);
     }
 
     function _approve(address to, uint256 tokenId) internal virtual {
         _tokenApprovals[tokenId] = to;
         emit Approval(LightSealerNFT.ownerOf(tokenId), to, tokenId);
     }
 }