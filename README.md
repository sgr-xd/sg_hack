# eVault Blockchain DApp

## Overview

The eVault DApp securely stores and manages legal files using Ethereum blockchain, IPFS, and Flask. It supports Admin and User roles with specific permissions, enforced through smart contracts.

## Architecture

- **Frontend**: React.js
- **Backend**: Flask (Python)
- **Blockchain**: Ethereum (Solidity, Truffle)
- **File Storage**: IPFS
- **Cloud Storage**: GCP Bucket for Legal Databases and backup
- **Database**: GCP for Legal Database, MongoDB
- **APIs**: Flask backend logic, connector APIs for GCP integration
- **Access Control**: Smart contracts
![alt text](file:///home/harish/Pictures/Screenshots/Screenshot%20from%202024-07-14%2016-30-42.png
 
## Components

### Smart Contracts

Manage document storage, retrieval, modification, deletion, ownership, and access control.

### Flask Backend

Handles HTTP requests, interacts with smart contracts, and manages file operations in IPFS and GCP.

### IPFS

Provides secure, distributed file storage with unique IPFS hashes.

### GCP Bucket

Offers centralized backup and storage for legal documents.

## User Roles and Permissions

### Admin

- View, update, add, delete all documents.
- Backup documents to GCP.
- Generate audit logs.
- Import/export documents from/to legal databases.

### User

- View, update, delete own documents.
- Export own data to legal databases.

## Unique Features

### Connector APIs

Connect IPFS data with GCP for seamless data export and import.

### Smart Contract RBAC

Enforces permissions via blockchain for transparency and security.

## Disaster Recovery and Backup

- Admin-triggered backups to GCP.
- Recover from MongoDB mappings and vault backups.

## Version Control and Change Tracking

- Tracks all document versions and changes, logging them on the blockchain.
- Provides a complete, tamper-proof audit trail.

## Security

- **Authentication**: Secure authentication using Fernet cryptographic algorithm.
- **Encryption**: Files encrypted before IPFS upload.
- **Audit Logs**: Comprehensive logs for traceability.
- **Backup**: Regular backups to GCP.

## Workflow

### Document Upload

1. Upload via frontend.
2. Store in IPFS, generate hash.
3. Smart contract logs metadata and hash.

### Document Retrieval

1. Request via frontend.
2. Backend retrieves hash via smart contract.
3. Fetch document from IPFS.

### Document Backup

1. Admin triggers backup.
2. Backend retrieves documents from IPFS.
3. Upload to GCP.
4. Log completion.

## Deployment

1. Deploy smart contracts with Truffle.
2. Set up Flask backend.
3. Run IPFS node.
4. Configure GCP bucket.
5. Host frontend.

## Future Enhancements

- Multi-factor authentication for Admins.
- Scalable microservices architecture with Kubernetes.

For detailed setup and usage, refer to the full documentation.
