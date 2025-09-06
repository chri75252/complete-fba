# Amazon FBA Agent System

An enterprise-grade automation platform for Amazon FBA product sourcing and profitability analysis. The system extracts products from supplier websites, matches them with Amazon listings, and calculates FBA profitability metrics to identify profitable arbitrage opportunities.

## Core Functionality

- **Automated Product Extraction**: Scrapes supplier websites for product data with configurable filtering
- **Amazon Product Matching**: Dual-strategy matching using EAN codes and title similarity scoring
- **FBA Financial Analysis**: Comprehensive ROI calculations including fees, VAT, and profit margins
- **Resumable Workflows**: State-managed processing that can resume from interruptions
- **Multi-Platform Support**: Native Windows and Linux/WSL compatibility

## Key Features

- **Smart Memory Management**: Sliding window approach preventing memory accumulation
- **File-Based Progress Tracking**: Zero-risk progress counting with multiple fallback methods
- **Browser Health Management**: Automatic Chrome restart and circuit breaker protection
- **Hash-Based Optimization**: O(1) duplicate prevention with 20-40% performance improvement
- **Atomic File Operations**: Windows-native atomic saves eliminating permission issues

The system is designed for marathon processing sessions (18+ hours) with comprehensive error handling and recovery mechanisms.