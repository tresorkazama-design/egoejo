import React, { useState, useEffect } from "react";
import { useSakaCycles } from "@/hooks/useSakaCycles";
import { useSakaSilo } from "@/hooks/useSakaSilo";
// import CompostNotification from "@/components/saka/CompostNotification"; // TODO: Créer ce composant
import { useEcoMode } from "@/contexts/EcoModeContext";
import { getSobrietyFeature } from "@/design-tokens";

export default function SakaSeasonsPage() {
  const { cycles, loading: loadingCycles, error: errorCycles } = useSakaCycles();
  const { silo, loading: loadingSilo, error: errorSilo } = useSakaSilo();
  const { sobrietyLevel } = useEcoMode();
  
  // Vérifier si animations sont activées selon le niveau de sobriété
  const canAnimate = getSobrietyFeature(sobrietyLevel, 'enableAnimations');
  
  // État pour la notification de compostage
  const [compostNotification, setCompostNotification] = useState<{
    amount: number;
    remainingBalance: number;
    siloBalance: number;
  } | null>(null);
  
  // Détecter un nouveau compostage (comparer avec état précédent)
  const [previousCompost, setPreviousCompost] = useState<number>(0);
  
  useEffect(() => {
    if (!silo) return;

    const currentCompost = silo.total_composted || 0;
    const newCompost = currentCompost - previousCompost;

    if (newCompost > 0) {
      // Nouveau compostage détecté
      setCompostNotification({
        amount: newCompost,
        remainingBalance: 0, // À récupérer depuis l'API utilisateur si nécessaire
        siloBalance: silo.total_balance || 0,
      });
      
      setPreviousCompost(currentCompost);
    }
  }, [silo, previousCompost]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Notification de compostage */}
      {compostNotification && (
        <div style={{ padding: '1rem', backgroundColor: 'var(--surface)', borderRadius: 'var(--radius)', marginBottom: '1rem' }}>
          <p>Compostage détecté : {compostNotification.amount} SAKA</p>
          <p>Solde restant : {compostNotification.remainingBalance} SAKA</p>
          <p>Silo Commun : {compostNotification.siloBalance} SAKA</p>
          <button onClick={() => setCompostNotification(null)}>Fermer</button>
        </div>
      )}

      <header className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          Saisons SAKA 🌾
        </h1>
        <p className="text-muted-foreground">
          Visualisez le cycle de vie des grains SAKA : récolte, plantation et régénération vers le Silo commun.
        </p>
      </header>

      {/* Bloc Silo commun */}
      <section className="rounded-2xl border p-4 md:p-6 bg-muted/40">
        <h2 className="text-xl font-semibold mb-2">Silo commun</h2>

        {loadingSilo && <p className="text-sm text-muted-foreground">Chargement du niveau du Silo…</p>}
        {errorSilo && (
          <p className="text-sm text-destructive">
            {errorSilo}
          </p>
        )}
        {silo && (
          <div className="flex items-baseline gap-4">
            <p className="text-3xl font-bold">
              {silo.total_balance.toLocaleString("fr-FR")} <span className="text-lg">grains</span>
            </p>
            {silo.last_compost_at && (
              <p className="text-xs text-muted-foreground">
                Dernière régénération : {new Date(silo.last_compost_at).toLocaleString("fr-FR")}
              </p>
            )}
          </div>
        )}
      </section>

      {/* Bloc Saisons / Cycles */}
      <section className="space-y-4">
        <div className="flex items-center justify-between gap-2">
          <h2 className="text-xl font-semibold">Saisons SAKA</h2>
        </div>

        {loadingCycles && <p className="text-sm text-muted-foreground">Chargement des cycles…</p>}
        {errorCycles && (
          <p className="text-sm text-destructive">
            {errorCycles}
          </p>
        )}

        {!loadingCycles && !errorCycles && cycles.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Aucun cycle SAKA n'a encore été enregistré.
          </p>
        )}

        <div className="space-y-3">
          {cycles.map((cycle) => (
            <article
              key={cycle.id}
              className="rounded-2xl border p-4 md:p-5 bg-background/60 flex flex-col md:flex-row md:items-center md:justify-between gap-4"
            >
              <div>
                <h3 className="text-base font-semibold">
                  {cycle.name}
                  {cycle.is_active && (
                    <span className="ml-2 text-xs px-2 py-1 bg-green-500/20 text-green-600 rounded-full">
                      Actif
                    </span>
                  )}
                </h3>
                <p className="text-xs text-muted-foreground">
                  {new Date(cycle.start_date).toLocaleDateString("fr-FR")} →{" "}
                  {new Date(cycle.end_date).toLocaleDateString("fr-FR")}
                </p>
              </div>

              <div className="grid grid-cols-3 gap-4 text-xs md:text-sm">
                <div>
                  <p className="font-medium">Récolté</p>
                  <p className="text-muted-foreground">
                    {cycle.stats?.saka_harvested?.toLocaleString("fr-FR") || 0} grains
                  </p>
                </div>
                <div>
                  <p className="font-medium">Planté</p>
                  <p className="text-muted-foreground">
                    {cycle.stats?.saka_planted?.toLocaleString("fr-FR") || 0} grains
                  </p>
                </div>
                <div>
                  <p className="font-medium">Régénéré</p>
                  <p className="text-muted-foreground">
                    {cycle.stats?.saka_composted?.toLocaleString("fr-FR") || 0} grains
                  </p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

