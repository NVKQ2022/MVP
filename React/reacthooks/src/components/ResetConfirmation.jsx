import { useRef, useEffect } from "react";

function ResetConfirmation({ onReset,isReset, setIsReset }) {
    const inputRef = useRef(null);
    const isConfirmed = useRef(false);

    useEffect(() => {
        if (isReset) {
            console.log("input bar focus")
            inputRef.current.focus();
        }
    }, [isReset]);

    const handleConfirmReset = () => {
        if (inputRef.current.value === "Confirm Reset") {
            isConfirmed.current = true;
            console.log("Confirmed:", isConfirmed.current);

            inputRef.current.value = ""

            onReset();
            setIsReset(false);
        } else {
            isConfirmed.current = false;
            console.log("Please type 'Confirm Reset'");
        }
    };

    return (
        <div>
            <input
                ref={inputRef}
                placeholder="Confirm Reset"
            />

            <button onClick={handleConfirmReset}>
                Confirm Reset
            </button>
        </div>
    );
}

export default ResetConfirmation;