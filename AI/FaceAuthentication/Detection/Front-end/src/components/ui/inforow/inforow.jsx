import { Label } from '@/components/ui/label/label';
import { Tooltip, TooltipTrigger, TooltipContent } from '@/components/ui/tooltip/tooltip';
import { cn } from '@/utils/cn';
import './inforow.scss';

function InfoRow({ label, value, truncate = false, className, ...props }) {
    const display = value ?? '—';

    return (
        <div data-slot="info-row" className={cn('info-row', className)} {...props}>
            <Label data-slot="info-row-label" className="info-row-label">
                {label}
            </Label>
            {truncate && value ? (
                <Tooltip>
                    <TooltipTrigger asChild>
                        <span data-slot="info-row-value" data-truncate="true" className="info-row-value">
                            {display}
                        </span>
                    </TooltipTrigger>
                    <TooltipContent>{value}</TooltipContent>
                </Tooltip>
            ) : (
                <span data-slot="info-row-value" className="info-row-value">
                    {display}
                </span>
            )}
        </div>
    );
}

export { InfoRow };