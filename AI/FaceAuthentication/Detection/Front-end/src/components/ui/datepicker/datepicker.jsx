import { cn } from '@/utils/cn';
import { CalendarDays } from 'lucide-react';
import './datepicker.scss';

function DatePicker({ value, onChange, disabled, className, id, ...props }) {
    return (
        <div data-slot="date-picker" className={cn('date-picker', className)}>
            <div className="date-picker__wrapper">
                <CalendarDays className="date-picker__icon" size={16} />
                <input
                    id={id}
                    type="date"
                    value={value}
                    onChange={onChange}
                    disabled={disabled}
                    className="date-picker__input"
                    onKeyDown={(e) => e.preventDefault()}
                    {...props}
                />
            </div>
        </div>
    );
}

export { DatePicker };