// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// Custom Errors
error NotOwner();
error ContractPaused();
error ZeroAmount();
error ZeroAddress();
error InsufficientVaultBalance();
error ExceedsCampaignBudget();
error TransferFailed();
error ReentrantCall();
error DepositTooSmall();

/**
 * @title CampaignVault
 * @dev Campaign maker deposits MON (native token) which the vault stores.
 *      Winners are paid native MON from the vault's balance.
 *      Built for Monad: 400ms blocks, 800ms finality, 50 gwei base fee.
 */
contract CampaignVault {
    address public owner;
    bool public paused;
    bool private _locked;

    // Campaign tracking
    uint256 public campaignBudget;     // Total MON deposited for this campaign
    uint256 public totalDistributed;   // Total MON paid out to winners
    uint256 public totalWinnersPaid;   // Number of payouts made
    uint256 public totalMonDeposited;  // Total MON received from campaign maker over lifetime

    // Per-user tracking
    mapping(address => uint256) public totalPaidToUser;
    mapping(address => uint256) public paymentCount;

    // Events
    event MonDeposited(address indexed depositor, uint256 monAmount, uint256 timestamp);
    event BountyPaid(address indexed winner, uint256 monAmount, uint256 totalPaidSoFar, uint256 timestamp);
    event VaultPaused(bool isPaused);
    event FundsWithdrawn(address indexed owner, uint256 amount);

    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }

    modifier whenNotPaused() {
        if (paused) revert ContractPaused();
        _;
    }

    modifier nonReentrant() {
        if (_locked) revert ReentrantCall();
        _locked = true;
        _;
        _locked = false;
    }

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Campaign maker deposits MON to fund the campaign.
     *      The deposited MON becomes the campaign budget for paying winners.
     */
    function deposit() external payable onlyOwner whenNotPaused nonReentrant {
        if (msg.value == 0) revert ZeroAmount();

        // Track
        totalMonDeposited += msg.value;
        campaignBudget += msg.value;

        emit MonDeposited(msg.sender, msg.value, block.timestamp);
    }

    /**
     * @dev Pay a winner their bounty in MON.
     *      Called by the Python backend agent via the owner wallet.
     */
    function payBounty(address winner, uint256 amount) external onlyOwner whenNotPaused nonReentrant {
        if (winner == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        if (address(this).balance < amount) revert InsufficientVaultBalance();
        if (totalDistributed + amount > campaignBudget) revert ExceedsCampaignBudget();

        totalDistributed += amount;
        totalPaidToUser[winner] += amount;
        paymentCount[winner] += 1;
        totalWinnersPaid += 1;

        // Native MON transfer
        (bool success, ) = payable(winner).call{value: amount}("");
        if (!success) revert TransferFailed();

        emit BountyPaid(winner, amount, totalDistributed, block.timestamp);
    }

    /**
     * @dev Emergency pause toggle.
     */
    function togglePause() external onlyOwner {
        paused = !paused;
        emit VaultPaused(paused);
    }

    /**
     * @dev Withdraw deposited MON back to owner (e.g. for leftover budget).
     */
    function withdrawMon(uint256 amount) external onlyOwner nonReentrant {
        if (address(this).balance < amount) revert InsufficientVaultBalance();
        (bool success, ) = payable(owner).call{value: amount}("");
        if (!success) revert TransferFailed();
        emit FundsWithdrawn(owner, amount);
    }

    /**
     * @dev View remaining native MON budget available for payouts.
     */
    function getRemainingBudget() external view returns (uint256) {
        if (campaignBudget <= totalDistributed) return 0;
        return campaignBudget - totalDistributed;
    }

    /**
     * @dev View the vault's MON (native) balance.
     */
    function getMonBalance() external view returns (uint256) {
        return address(this).balance;
    }

    receive() external payable {
        // Automatically add plain transfers to the budget
        totalMonDeposited += msg.value;
        campaignBudget += msg.value;
        emit MonDeposited(msg.sender, msg.value, block.timestamp);
    }
}
