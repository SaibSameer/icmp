import React, { createContext, useState, useContext } from 'react';

const BusinessContext = createContext();

export const useBusinessContext = () => useContext(BusinessContext);

export const BusinessProvider = ({ children }) => {
    const [selectedBusinessId, setSelectedBusinessId] = useState(null);

    const value = {
        selectedBusinessId,
        setSelectedBusinessId,
    };

    return (
        <BusinessContext.Provider value={value}>
            {children}
        </BusinessContext.Provider>
    );
};