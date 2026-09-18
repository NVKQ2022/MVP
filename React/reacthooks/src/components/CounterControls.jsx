import { useState } from 'react'
import ResetConfirmation from './ResetConfirmation';
function CounterControls({
    onIncrement,
    onDecrement,
    onReset
}) {
    const [isReset, setIsReset] = useState(false);

    function onResetClick() {
         setIsReset(true)
    }
    return (
        <div className="controls">
            <div className="counter-buttons">
                <button onClick={onIncrement}>
                    +1
                </button>

                <button onClick={onDecrement}>
                    -1
                </button>

                <button onClick={onResetClick}>
                    Reset
                </button>
            </div>

            <ResetConfirmation
                onReset={onReset}
                isReset={isReset}
                setIsReset={setIsReset}
            />
        </div>
    );
}

export default CounterControls;
