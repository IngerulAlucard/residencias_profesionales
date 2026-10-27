(() => {
    const SUPABASE_URL = 'https://deaeuvtvlnwtoltwftxs.supabase.co';
    const SUPABASE_PUBLISHABLE_KEY = 'sb_publishable_HHYdPwYaTrfXwvXopHESYA_YPIHEGT0';

    if (!window.supabase || SUPABASE_URL.includes('TU_PROJECT_REF') ||
        SUPABASE_PUBLISHABLE_KEY.includes('TU_CLAVE')) {
        console.error('Completa js/supabase-config.js con los datos de tu proyecto Supabase.');
        return;
    }

    window.supabaseClient = window.supabase.createClient(
        SUPABASE_URL,
        SUPABASE_PUBLISHABLE_KEY
    );
})();
