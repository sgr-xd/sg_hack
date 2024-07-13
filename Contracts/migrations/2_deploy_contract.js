const fs = require('fs');
const path = require('path');
const DocumentVault = artifacts.require("DocumentVault");

module.exports = function(deployer) {
  deployer.deploy(DocumentVault).then(() => {
    const contractInfo = {
      address: DocumentVault.address,
      abi: DocumentVault.abi
    };

    const jsonString = JSON.stringify(contractInfo, null, 2);
    const filePath = path.join(__dirname, '../Contracts/contract_info.json');
    fs.writeFileSync(filePath, jsonString);

    console.log("Contract info saved to contract_info.json");
  });
};
