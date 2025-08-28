# **EtherCS** 

EtherCS is a peer-to-peer CS2 (Counter-Strike 2) asset marketplace built with a backend-first approach, focusing on **efficiency, clean data handling, and extensibility**. It is designed to move from a working MVP to a scalable marketplace with blockchain integration.  

## Stack & Systems  
- **Flask (Python)** backend with a minimalistic structure (all `.py` kept at root for clarity).  
- **MySQL** for structured storage of users, assets, listings, and transactions.  
- **Frontend:** started with HTML forms → progressively integrating **AJAX + JavaScript** for async flows.  
- **Web3 integration:** smart contracts, using solidity, for escrow-style buy/sell.  
- **Browser extension (separate repo):** automates Steam trades via background API calls.  

## Core Features  
- Steam OpenID login & inventory fetching.
- User's assets are automatically fetched server-side then displayed using Steam's API.
- Users can list items, set/edit prices, and manage personal listings.  
- Global marketplace view with live sync between trades and listings.  
- Transaction lifecycle handled server-side: *Pending → TradeSent → Success/Failure*. 
- User's MetaMask wallet can connect to platform. 
- Mock payment system now; blockchain wallet escrow is planned.  

## Development Approach  
- Built in **phases**: get functionality working first, then refactor/abstract.  
- Backend-first mindset — database design and transaction safety prioritized over UI polish.  
- Pragmatic and iterative: start simple (forms, tuples) → expand into async flows, abstraction, and smart contracts.  
- Always geared toward **real-world scalability**, even with a simple front-end.  

---