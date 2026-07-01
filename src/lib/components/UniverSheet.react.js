import React, {useEffect, useRef} from 'react';
import PropTypes from 'prop-types';
import {createUniver, LocaleType, mergeLocales} from '@univerjs/presets';
import {UniverSheetsCorePreset} from '@univerjs/preset-sheets-core';
import UniverPresetSheetsCoreEnUS from '@univerjs/preset-sheets-core/locales/en-US';
import '@univerjs/preset-sheets-core/lib/index.css';

/**
 * UniverSheet renders a Univer spreadsheet (https://univer.ai) inside a Dash app.
 *
 * The `data` prop is the workbook (Univer's IWorkbookData as a plain dict) and
 * round-trips in both directions: user edits emit a debounced full snapshot back
 * to Dash callbacks, and setting `data` from a callback re-renders the sheet.
 */
export default function UniverSheet(props) {
    const {id, data, style, className, debounce, setProps} = props;

    const containerRef = useRef(null);
    const apiRef = useRef(null); // FUniver (univerAPI)
    const univerRef = useRef(null); // Univer instance
    // JSON string of the last snapshot we pushed to Dash. Lets the data-prop effect
    // tell "this change came from us" (skip) from "Dash/user set new data" (rebuild),
    // which is what prevents an edit -> setProps -> data -> rebuild feedback loop.
    const lastEmittedRef = useRef(null);

    // Mount Univer once. Univer runs its own isolated React root inside the div,
    // so it never touches Dash's React tree.
    useEffect(() => {
        const {univer, univerAPI} = createUniver({
            locale: LocaleType.EN_US,
            locales: {
                [LocaleType.EN_US]: mergeLocales(UniverPresetSheetsCoreEnUS),
            },
            presets: [
                UniverSheetsCorePreset({container: containerRef.current}),
            ],
        });
        univerRef.current = univer;
        apiRef.current = univerAPI;
        // Expose the Univer Facade API on the container node. Univer renders to a
        // canvas, so this is how e2e tests (and power users) reach the workbook
        // programmatically. ponytail: cheap handle, not a promise-of-stability API.
        if (containerRef.current) {
            containerRef.current.univerAPI = univerAPI;
        }

        univerAPI.createWorkbook(data || {});
        lastEmittedRef.current = JSON.stringify(data || {});

        let timer = null;
        const emit = () => {
            const wb = univerAPI.getActiveWorkbook();
            if (!wb) {
                return;
            }
            const snapshot = wb.save();
            lastEmittedRef.current = JSON.stringify(snapshot);
            if (setProps) {
                setProps({data: snapshot});
            }
        };
        const disposable = univerAPI.addEvent(
            univerAPI.Event.SheetValueChanged,
            () => {
                if (timer) {
                    clearTimeout(timer);
                }
                timer = setTimeout(emit, debounce);
            }
        );

        return () => {
            if (timer) {
                clearTimeout(timer);
            }
            try {
                disposable.dispose();
            } catch (e) {
                // already disposed
            }
            try {
                univer.dispose();
            } catch (e) {
                // already disposed
            }
        };
        // Mount-only: `data` and `debounce` are read fresh via refs/closure at call
        // time; later `data` changes are handled by the effect below.
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Apply `data` changes that originate outside the component (a Dash callback
    // writing Output('...','data')). Skip echoes of our own snapshots.
    useEffect(() => {
        const univerAPI = apiRef.current;
        if (!univerAPI) {
            return; // not mounted yet; initial data handled on mount
        }
        if (JSON.stringify(data) === lastEmittedRef.current) {
            return; // this is the snapshot we just emitted — no rebuild
        }
        const current = univerAPI.getActiveWorkbook();
        if (current) {
            univerAPI.disposeUnit(current.getId());
        }
        univerAPI.createWorkbook(data || {});
        lastEmittedRef.current = JSON.stringify(data || {});
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [data]);

    return (
        <div
            id={id}
            ref={containerRef}
            className={className}
            style={{height: '500px', width: '100%', ...style}}
        />
    );
}

UniverSheet.defaultProps = {
    debounce: 300,
};

UniverSheet.propTypes = {
    /** The ID used to identify this component in Dash callbacks. */
    id: PropTypes.string,

    /**
     * The workbook contents as Univer's IWorkbookData (a plain object). Updated
     * (debounced) as the user edits, and re-rendered when set from a callback.
     */
    data: PropTypes.object,

    /** Inline styles for the container div. Defaults to full width, 500px tall. */
    style: PropTypes.object,

    /** CSS class for the container div. */
    className: PropTypes.string,

    /** Milliseconds to debounce edit -> `data` updates sent to Dash. Default 300. */
    debounce: PropTypes.number,

    /**
     * Dash-assigned callback that updates props. Called with `{data: snapshot}`
     * on edits so the new workbook state is available to callbacks.
     */
    setProps: PropTypes.func,
};
