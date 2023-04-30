import React, { useEffect, useState } from 'react'
import '../App.css';

export default function HealthStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [health, setHealth] = useState({});
    const [error, setError] = useState(null)

    const getHealth = () => {

        fetch(`http://localhost:8120/health`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received health stats")
                setHealth(result);
                setIsLoaded(true);
            }, (error) => {
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
        const interval = setInterval(() => getHealth(), 5000); // Update every 5 seconds
        return () => clearInterval(interval);
    }, [getHealth]);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false) {
        return (<div>Loading...</div>)
    } else if (isLoaded === true) {
        return (
            <div>
                <h1>Latest Health</h1>
                <table className={"HealthTable"}>
                    <tbody>
                        <tr>
                            <th>Health</th>
                        </tr>
                        <tr>
                            <td>Receiver: {health['receiver']}</td>
                        </tr>
                        <tr>
                            <td>Storage: {health['storage']}</td>
                        </tr>
                        <tr>
                            <td>Processor: {health['processor']}</td>
                        </tr>
                        <tr>
                            <td >Audit: {health['audit']}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {health['last_updated']}</h3>
            </div>
        )
    }
}
