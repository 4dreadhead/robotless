const PROPS = ['VERSION', 'SHADING_LANGUAGE_VERSION', 'VENDOR', 'RENDERER', 'MAX_VERTEX_ATTRIBS',
               'MAX_VERTEX_UNIFORM_VECTORS', 'MAX_VERTEX_TEXTURE_IMAGE_UNITS', 'MAX_VARYING_VECTORS',
               'MAX_VERTEX_UNIFORM_COMPONENTS', 'MAX_VERTEX_UNIFORM_BLOCKS', 'MAX_VERTEX_OUTPUT_COMPONENTS',
               'MAX_VARYING_COMPONENTS', 'MAX_TRANSFORM_FEEDBACK_INTERLEAVED_COMPONENTS',
               'MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS', 'MAX_TRANSFORM_FEEDBACK_SEPARATE_COMPONENTS',
               'ALIASED_LINE_WIDTH_RANGE', 'ALIASED_POINT_SIZE_RANGE', 'MAX_FRAGMENT_UNIFORM_VECTORS',
               'MAX_TEXTURE_IMAGE_UNITS', 'MAX_FRAGMENT_UNIFORM_COMPONENTS', 'MAX_FRAGMENT_UNIFORM_BLOCKS',
               'MAX_FRAGMENT_INPUT_COMPONENTS', 'MIN_PROGRAM_TEXEL_OFFSET', 'MAX_PROGRAM_TEXEL_OFFSET',
               'MAX_DRAW_BUFFERS', 'MAX_COLOR_ATTACHMENTS', 'MAX_SAMPLES', 'MAX_RENDERBUFFER_SIZE',
               'MAX_VIEWPORT_DIMS', 'RED_BITS', 'GREEN_BITS', 'BLUE_BITS', 'ALPHA_BITS', 'DEPTH_BITS',
               'STENCIL_BITS', 'MAX_TEXTURE_SIZE', 'MAX_CUBE_MAP_TEXTURE_SIZE',
               'MAX_COMBINED_TEXTURE_IMAGE_UNITS', 'MAX_3D_TEXTURE_SIZE', 'MAX_ARRAY_TEXTURE_LAYERS',
               'MAX_TEXTURE_LOD_BIAS', 'MAX_UNIFORM_BUFFER_BINDINGS', 'MAX_UNIFORM_BLOCK_SIZE',
               'UNIFORM_BUFFER_OFFSET_ALIGNMENT', 'MAX_COMBINED_UNIFORM_BLOCKS',
               'MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS', 'MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS']
function webglAnalyzer() {
    let canvas, context, contextAttributes, shaderPrecision,
        supportedContexts = [
            "webgl2", "experimental-webgl2", "webgl", "experimental-webgl", "moz-webgl", "webkit-3d", "webgl2-compute"
        ], contextData = {}, supportedContextsList = [], hasWebGL1 = false,
        hasWebGL2 = false, isWebGL1Used = false, isWebGL2Used = false;
    for (let index in supportedContexts) {
        let contextType = supportedContexts[index];
        let debugExt;
        let contextInfo = function(type) {
            (canvas = document.createElement("canvas")).width = 256;
            canvas.height = 128;
            canvas.style.backgroundColor = "#fafafa";
            canvas.style.borderRadius = "4px";
            let context = canvas.getContext(type);
            if (!context)
                return false;
            hasWebGL1 = hasWebGL1 || context;
            let contextVersion = -1 !== type.indexOf("2") ? 2 : 1;
            contextData[type] = (isWebGL2Used || contextVersion !== 1 ? (isWebGL1Used || contextVersion !== 2 ||
                (isWebGL1Used = context)) : isWebGL2Used = context, {});
            PROPS.forEach(function(propName) {
                let propValue = context.getParameter(context[propName]);
                if (propValue !== null) {
                    contextData[type][propName] = propValue;
                }
            });
            contextAttributes = context.getContextAttributes();
            if (typeof contextAttributes === "object" && Object.keys(contextAttributes).length > 0) {
                Object.assign(contextData[type], contextAttributes);
            }
            contextData[type].drawingBufferColorSpace = context.drawingBufferColorSpace;
            contextData[type].unpackColorSpace = context.unpackColorSpace;
            let debugRendererInfo = context.getExtension("WEBGL_debug_renderer_info");
            if (debugRendererInfo) {
                contextData[type].UNMASKED_RENDERER_WEBGL = context.
                    getParameter(debugRendererInfo.UNMASKED_RENDERER_WEBGL);
                contextData[type].UNMASKED_VENDOR_WEBGL = context.
                    getParameter(debugRendererInfo.UNMASKED_VENDOR_WEBGL);
            }
            contextData[type].VERTEX_SHADER = getShaderInfo(context, context.VERTEX_SHADER);
            contextData[type].FRAGMENT_SHADER = getShaderInfo(context, context.FRAGMENT_SHADER);
            contextData[type].HIGH_FLOAT_HIGH_INT = function(context) {
                try {
                    let fragmentShaderPrecision = context.
                        getShaderPrecisionFormat(context.FRAGMENT_SHADER, context.HIGH_FLOAT);
                    return (fragmentShaderPrecision.precision !== 0 ? "highp/" : "mediump/") +
                           (fragmentShaderPrecision.rangeMax !== 0 ? "highp" : "lowp");
                } catch (e) {
                    return "n/a";
                }
            }(context);
            contextData[type].MAX_DRAW_BUFFERS_WEBGL = shaderPrecision = null != (debugExt = context.
                getExtension("WEBGL_draw_buffers")) ?
                context.getParameter(debugExt.MAX_DRAW_BUFFERS_WEBGL) :
                shaderPrecision;
            contextData[type].MAX_TEXTURE_MAX_ANISOTROPY_EXT = shaderPrecision = (debugExt = context.
                getExtension("EXT_texture_filter_anisotropic") ||
                context.getExtension("WEBKIT_EXT_texture_filter_anisotropic") ||
                context.getExtension("MOZ_EXT_texture_filter_anisotropic")) ?
                context.getParameter(debugExt.MAX_TEXTURE_MAX_ANISOTROPY_EXT) :
                shaderPrecision;
            contextData[type].extensions = context.getSupportedExtensions();
            return contextData[type];
        }(supportedContexts[index]);
        if (contextInfo) { supportedContextsList.push(supportedContexts[index]); }
    }
    let successEvent = new Event('webglAnalyzed');
    successEvent.fingerprint = JSON.stringify(contextData);
    successEvent.fingerprintHash = window.CryptoJS.SHA256(successEvent.fingerprint).toString();
    window.dispatchEvent(successEvent);
}
function getShaderInfo(context, shaderType) {
    let highFloatPrecision = context.getShaderPrecisionFormat(shaderType, context.HIGH_FLOAT);
    let mediumFloatPrecision = context.getShaderPrecisionFormat(shaderType, context.MEDIUM_FLOAT);
    return (context = highFloatPrecision.precision === 0 ? mediumFloatPrecision : highFloatPrecision) ?
        "[-2^" + context.rangeMin + ",2^" + context.rangeMax + "](" + context.precision + ")" :
        undefined;
}

window.addEventListener('analyzeWebgl', function () { webglAnalyzer(); });
