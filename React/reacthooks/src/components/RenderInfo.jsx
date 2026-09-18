function RenderInfo({ previousCount, renderCount }) {
    return (
        <div className="render-info">
            <p>Previous count: {previousCount}</p>
            <p>Render count: {renderCount}</p>
        </div>
    );
}


export default RenderInfo;