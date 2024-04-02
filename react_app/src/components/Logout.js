import React from 'react';

function Logout({ setToken, setRecommendations}) {
    const handleLogout = async () => {
        try {
            await fetch('/auth/logout');
            setToken('');
            setRecommendations([]);
        } catch (error) {
            console.error('Error logging out', error);
        }
    };

    return (
        <button className="logout-btn logout-position" onClick={handleLogout}>Logout</button>
    );
}

export default Logout;